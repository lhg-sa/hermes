import frappe
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Guatemala timezone (GMT-6)
GT_TIMEZONE = ZoneInfo('America/Guatemala')

def get_guatemala_today():
    """Get today's date in Guatemala timezone (GMT-6)"""
    return datetime.now(GT_TIMEZONE).date()

@frappe.whitelist(allow_guest=True)
def get_app():
    """Serve the Hermes PWA app"""
    # Get the built HTML file
    app_path = os.path.join(os.path.dirname(__file__), '..', 'public', 'build', 'index.html')
    
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            return frappe.make_formatted_html(f.read())
    
    # Fallback: return a simple message if build doesn't exist yet
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hermes</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <div style="padding: 20px; text-align: center; font-family: sans-serif;">
            <h1>Hermes App</h1>
            <p>La aplicación está siendo configurada. Por favor ejecute:</p>
            <code>cd apps/hermes/frontend && npm install && npm run build</code>
        </div>
    </body>
    </html>
    """

@frappe.whitelist(allow_guest=True)
def check_session():
    """Check if user has a valid session"""
    user = frappe.session.user
    return {
        'user': user,
        'authenticated': user != 'Guest'
    }

@frappe.whitelist()
def get_rooms():
    """Get all enabled rooms"""
    # Check if user is logged in
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    rooms = frappe.db.sql("""
        SELECT name, habitacion, distribucion, costo
        FROM `tabroom`
        WHERE habilitado = 1
        ORDER BY habitacion
    """, as_dict=True)
    return rooms

@frappe.whitelist()
def get_week_availability(start_date=None):
    """Get room availability for a week starting from start_date"""
    # Check if user is logged in
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    # Use Guatemala timezone for today
    guatemala_today = get_guatemala_today()
    
    if not start_date:
        start_date = get_monday(guatemala_today)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        # Ensure we start from Monday
        start_date = get_monday(start_date)
    
    end_date = start_date + timedelta(days=7)
    
    # Get all enabled rooms
    rooms = frappe.db.sql("""
        SELECT name, habitacion, distribucion
        FROM `tabroom`
        WHERE habilitado = 1
        ORDER BY habitacion
    """, as_dict=True)
    
    # Get reservations that overlap with the week
    reservations = frappe.db.sql("""
        SELECT 
            r.name as reservation_id,
            r.fecha_entrada,
            r.fecha_salida,
            r.estado_reserva,
            r.cliente,
            c.customer_name,
            rd.habitacion
        FROM `tabreservation` r
        LEFT JOIN `tabCustomer` c ON c.name = r.cliente
        LEFT JOIN `tabreservation_detail` rd ON rd.parent = r.name
        WHERE r.fecha_salida >= %s 
        AND r.fecha_entrada < %s
        AND r.estado_reserva NOT IN ('NO SHOW')
        AND rd.habitacion IS NOT NULL
    """, (start_date, end_date), as_dict=True)
    
    # Build availability matrix
    availability = {}
    for room in rooms:
        availability[room.name] = {
            'room_name': room.habitacion,
            'distribution': room.distribucion or '',
            'full_name': f"{room.habitacion} - {room.distribucion}" if room.distribucion else room.habitacion,
            'days': {}
        }
        
        # Initialize all days as free (Monday to Sunday = 7 days)
        current_date = start_date
        for i in range(7):
            availability[room.name]['days'][current_date.isoformat()] = {
                'status': 'free',
                'reservation': None
            }
            current_date += timedelta(days=1)
    
    # Fill in reservations
    for res in reservations:
        room_name = res.habitacion
        if room_name in availability:
            current_date = max(res.fecha_entrada, start_date)
            end = min(res.fecha_salida, end_date)
            
            while current_date < end:
                date_str = current_date.isoformat()
                if date_str in availability[room_name]['days']:
                    status = map_status(res.estado_reserva)
                    availability[room_name]['days'][date_str] = {
                        'status': status,
                        'reservation': {
                            'id': res.reservation_id,
                            'customer': res.customer_name,
                            'status': res.estado_reserva
                        }
                    }
                current_date += timedelta(days=1)
    
    # Calculate totals per day (Monday to Sunday = 7 days)
    totals = {}
    current_date = start_date
    for i in range(7):
        date_str = current_date.isoformat()
        totals[date_str] = {
            'tentative': 0,
            'unpaid': 0,
            'paid': 0,
            'noshow': 0,
            'free': 0
        }
        
        for room_name, room_data in availability.items():
            status = room_data['days'][date_str]['status']
            totals[date_str][status] += 1
        
        current_date += timedelta(days=1)
    
    # Generate week info
    week_info = generate_week_info(start_date)
    
    return {
        'rooms': availability,
        'totals': totals,
        'week_info': week_info,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }

def get_monday(date):
    """Get the Monday of the week for a given date"""
    return date - timedelta(days=date.weekday())

def map_status(estado_reserva):
    """Map reservation status to availability status"""
    status_map = {
        'RESERVA PAGADA': 'paid',
        'RESERVA SIN PAGO': 'unpaid',
        'TENTATIVO': 'tentative',
        'NO SHOW': 'noshow'
    }
    return status_map.get(estado_reserva, 'free')

def generate_week_info(start_date):
    """Generate week information for header (Monday to Sunday = 7 days)"""
    days = []
    day_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    current_date = start_date
    # Use Guatemala timezone for today comparison
    today = get_guatemala_today()
    
    for i in range(7):
        days.append({
            'date': current_date.isoformat(),
            'day_name': day_names[current_date.weekday()],
            'day_number': current_date.day,
            'is_today': current_date == today
        })
        current_date += timedelta(days=1)
    
    # Calculate month and week numbers
    end_date = start_date + timedelta(days=6)
    month_name = get_month_name(start_date.month)
    
    # Get week numbers
    week1 = start_date.isocalendar()[1]
    week2 = end_date.isocalendar()[1]
    
    weeks_str = f"Semana {week1}"
    if week2 != week1:
        weeks_str += f" - {week2}"
    
    return {
        'month': month_name,
        'year': start_date.year,
        'weeks': weeks_str,
        'days': days
    }

def get_month_name(month):
    """Get Spanish month name"""
    months = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return months[month - 1]

@frappe.whitelist()
def get_reservation_details(reservation_id):
    """Get detailed information about a reservation"""
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    # Get reservation details
    reservation = frappe.db.sql("""
        SELECT 
            r.name as reservation_id,
            r.fecha_entrada,
            r.fecha_salida,
            r.estado_reserva,
            r.cliente,
            r.notas,
            r.total_global,
            r.total_abonado,
            r.total_pendiente,
            r.creation,
            r.customer_name,
            r.telefono
        FROM `tabreservation` r
        WHERE r.name = %s
    """, (reservation_id,), as_dict=True)
    
    if not reservation:
        return None
    
    reservation = reservation[0]
    
    # Get room details
    rooms = frappe.db.sql("""
        SELECT 
            rd.habitacion,
            rd.nota,
            rd.precio_base,
            rd.total_estadia
        FROM `tabreservation_detail` rd
        WHERE rd.parent = %s
    """, (reservation_id,), as_dict=True)
    
    reservation['rooms'] = rooms
    
    # Format dates
    if reservation.get('fecha_entrada'):
        reservation['fecha_entrada_formatted'] = reservation['fecha_entrada'].strftime('%d/%m/%Y')
    if reservation.get('fecha_salida'):
        reservation['fecha_salida_formatted'] = reservation['fecha_salida'].strftime('%d/%m/%Y')
    if reservation.get('creation'):
        reservation['creation_formatted'] = reservation['creation'].strftime('%d/%m/%Y %H:%M')
    
    # Calculate nights
    if reservation.get('fecha_entrada') and reservation.get('fecha_salida'):
        nights = (reservation['fecha_salida'] - reservation['fecha_entrada']).days
        reservation['nights'] = nights
    
    # Map status to Spanish
    status_map = {
        'RESERVA PAGADA': 'Pagada',
        'RESERVA SIN PAGO': 'Sin Pago',
        'TENTATIVO': 'Tentativo',
        'NO SHOW': 'No Show'
    }
    reservation['estado_formatted'] = status_map.get(reservation.get('estado_reserva'), reservation.get('estado_reserva'))
    
    return reservation


@frappe.whitelist()
def get_reservations_list():
    """Get list of all reservations"""
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    reservations = frappe.db.sql("""
        SELECT 
            r.name,
            r.fecha_entrada,
            r.fecha_salida,
            r.estado_reserva,
            r.customer_name,
            r.total_global,
            (SELECT COUNT(*) FROM `tabreservation_detail` rd WHERE rd.parent = r.name) as rooms_count
        FROM `tabreservation` r
        ORDER BY r.creation DESC
        LIMIT 100
    """, as_dict=True)
    
    return reservations or []


@frappe.whitelist()
def get_available_rooms():
    """Get list of all rooms with their base prices"""
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    rooms = frappe.db.sql("""
        SELECT 
            name,
            habitacion as full_name,
            costo as precio_base
        FROM `tabroom`
        WHERE habilitado = 1 OR habilitado IS NULL
        ORDER BY habitacion
    """, as_dict=True)
    
    return rooms or []


@frappe.whitelist()
def get_available_rooms_for_dates(fecha_entrada, fecha_salida):
    """Get rooms available for specific date range"""
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    if not fecha_entrada or not fecha_salida:
        return []
    
    # Get all enabled rooms
    all_rooms = frappe.db.sql("""
        SELECT 
            name,
            habitacion as full_name,
            costo as precio_base
        FROM `tabroom`
        WHERE habilitado = 1 OR habilitado IS NULL
        ORDER BY habitacion
    """, as_dict=True) or []
    
    # Get rooms that are occupied in the date range
    # A room is occupied if there's any reservation that overlaps with the requested dates
    # Overlap condition: fecha_entrada < existing_salida AND fecha_salida > existing_entrada
    occupied_rooms = frappe.db.sql("""
        SELECT DISTINCT rd.habitacion
        FROM `tabreservation_detail` rd
        JOIN `tabreservation` r ON r.name = rd.parent
        WHERE r.docstatus < 2
        AND r.estado_reserva IN ('TENTATIVO', 'RESERVA SIN PAGO', 'RESERVA PAGADA')
        AND %s < r.fecha_salida
        AND %s > r.fecha_entrada
    """, (fecha_entrada, fecha_salida), as_dict=True)
    
    occupied_room_names = [r.habitacion for r in occupied_rooms]
    
    # Filter out occupied rooms
    available_rooms = [room for room in all_rooms if room.name not in occupied_room_names]
    
    return available_rooms


@frappe.whitelist()
def search_customers(search):
    """Search for customers by name"""
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    if not search or len(search) < 2:
        return []
    
    customers = frappe.db.sql("""
        SELECT 
            name,
            customer_name
        FROM `tabCustomer`
        WHERE customer_name LIKE %s
        AND disabled = 0
        ORDER BY customer_name
        LIMIT 20
    """, (f'%{search}%',), as_dict=True)
    
    return customers or []


@frappe.whitelist()
def create_reservation(cliente, fecha_entrada, fecha_salida, habitacion, precio_base, estado_reserva='TENTATIVO', notas=''):
    """Create a new reservation"""
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    # Calculate nights and total
    start_date = datetime.strptime(fecha_entrada, '%Y-%m-%d').date()
    end_date = datetime.strptime(fecha_salida, '%Y-%m-%d').date()
    nights = (end_date - start_date).days
    
    if nights <= 0:
        frappe.throw('La fecha de salida debe ser posterior a la fecha de entrada')
    
    total = float(precio_base) * nights
    
    # Get customer name
    customer_name = frappe.db.get_value('Customer', cliente, 'customer_name')
    
    # Create reservation
    reservation = frappe.new_doc('reservation')
    reservation.cliente = cliente
    reservation.customer_name = customer_name
    reservation.fecha_entrada = fecha_entrada
    reservation.fecha_salida = fecha_salida
    reservation.estado_reserva = estado_reserva
    reservation.notas = notas
    reservation.total_global = total
    reservation.total_abonado = 0
    reservation.total_pendiente = total
    
    # Add room detail
    reservation.append('reserva_detalle', {
        'habitacion': habitacion,
        'precio_base': precio_base,
        'total_estadia': total
    })
    
    reservation.insert()
    frappe.db.commit()
    
    return {'success': True, 'reservation_id': reservation.name}


@frappe.whitelist()
def create_customer(customer_name):
    """Create a new customer"""
    if frappe.session.user == 'Guest':
        frappe.throw('Not authenticated', frappe.PermissionError)
    
    if not customer_name or not customer_name.strip():
        frappe.throw('El nombre del cliente es requerido')
    
    # Check if customer already exists
    existing = frappe.db.get_value('Customer', {'customer_name': customer_name.strip()}, 'name')
    if existing:
        return {'name': existing, 'customer_name': customer_name.strip()}
    
    # Create new customer
    customer = frappe.new_doc('Customer')
    customer.customer_name = customer_name.strip()
    customer.customer_type = 'Individual'
    customer.insert()
    frappe.db.commit()
    
    return {'name': customer.name, 'customer_name': customer.customer_name}
