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
    """Serve the Hermes PWA app with cache busting"""
    import time
    import traceback
    
    try:
        # Path to built files
        app_path = os.path.join(os.path.dirname(__file__), 'public', 'hermes', 'index.html')
        
        # Generate version from file modification time
        version = int(os.path.getmtime(app_path)) if os.path.exists(app_path) else int(time.time())
        
        if os.path.exists(app_path):
            with open(app_path, 'r') as f:
                html_content = f.read()
                
                # Inject version meta tag
                version_tag = f'<meta name="hermes-version" content="{version}">'
                if '<head>' in html_content:
                    html_content = html_content.replace('<head>', f'<head>\n    {version_tag}')
                
                # Add version query param to assets
                html_content = html_content.replace('.js"', f'.js?v={version}"')
                html_content = html_content.replace('.css"', f'.css?v={version}"')
                
                return html_content
        
        # Fallback
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Hermes</title></head>
        <body><h1>Build not found</h1></body>
        </html>
        """
    except Exception as e:
        frappe.log_error(f"Hermes get_app error: {str(e)}\n{traceback.format_exc()}", "Hermes Error")
        return f"Error: {str(e)}"
    
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

@frappe.whitelist(allow_guest=True)
def get_rooms():
    """Get all enabled rooms"""
    # Check authentication
    if frappe.session.user == 'Guest':
        return []
    
    rooms = frappe.db.sql("""
        SELECT name, habitacion, distribucion, costo
        FROM `tabroom`
        WHERE habilitado = 1
        ORDER BY habitacion
    """, as_dict=True)
    return rooms

@frappe.whitelist(allow_guest=True)
def get_week_availability(start_date=None):
    """Get room availability for a week starting from start_date"""
    # Check authentication
    if frappe.session.user == 'Guest':
        return {'rooms': {}, 'totals': {}, 'week_info': {'days': [], 'month': '', 'year': '', 'weeks': ''}, 'start_date': None}
    
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

@frappe.whitelist(allow_guest=True)
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


@frappe.whitelist(allow_guest=True)
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


@frappe.whitelist(allow_guest=True)
def search_customers(search):
    """Search for customers by name"""
    # Check authentication
    if frappe.session.user == 'Guest':
        return []
    
    # If search is empty or too short, return all customers
    if not search or len(search) < 1:
        customers = frappe.db.sql("""
            SELECT 
                name,
                customer_name
            FROM `tabCustomer`
            ORDER BY customer_name
            LIMIT 50
        """, as_dict=True)
        return customers or []
    
    customers = frappe.db.sql("""
        SELECT 
            name,
            customer_name
        FROM `tabCustomer`
        WHERE customer_name LIKE %s
        ORDER BY customer_name
        LIMIT 20
    """, (f'%{search}%',), as_dict=True)
    
    return customers or []


@frappe.whitelist(allow_guest=True)
def create_reservation(cliente, customer_name, fecha_entrada, fecha_salida, habitacion, precio_base, estado_reserva='TENTATIVO', total_abonado=0, notas=''):
    """Create a new reservation"""
    # Check authentication
    if frappe.session.user == 'Guest':
        return {'success': False, 'error': 'Not authenticated'}
    
    # Calculate nights and total
    start_date = datetime.strptime(fecha_entrada, '%Y-%m-%d').date()
    end_date = datetime.strptime(fecha_salida, '%Y-%m-%d').date()
    nights = (end_date - start_date).days
    
    if nights <= 0:
        frappe.throw('La fecha de salida debe ser posterior a la fecha de entrada')
    
    total = float(precio_base) * nights
    
    # Handle total_abonado
    try:
        total_abonado = float(total_abonado) if total_abonado else 0
    except (ValueError, TypeError):
        total_abonado = 0
    
    # Get customer name
    customer_name = customer_name or frappe.db.get_value('Customer', cliente, 'customer_name')
    
    # Create reservation
    reservation = frappe.new_doc('reservation')
    reservation.cliente = cliente
    reservation.customer_name = customer_name
    reservation.fecha_entrada = fecha_entrada
    reservation.fecha_salida = fecha_salida
    reservation.estado_reserva = estado_reserva
    reservation.notas = notas
    reservation.total_global = total
    reservation.total_abonado = total_abonado
    reservation.total_pendiente = total - total_abonado
    reservation.test = customer_name
    
    # Add room detail
    reservation.append('reserva_detalle', {
        'habitacion': habitacion,
        'precio_base': precio_base,
        'total_estadia': total
    })
    
    reservation.insert(ignore_permissions=True)
    frappe.db.commit()

    saved_reservation = frappe.get_doc('reservation', reservation.name)

    return {
        'success': True, 
        'reservation_id': reservation.name,
        'total_abonado': saved_reservation.total_abonado,
        'test': saved_reservation.test,
        'total_pendiente': saved_reservation.total_pendiente,
        'total_global': saved_reservation.total_global
    }


@frappe.whitelist(allow_guest=True)
def debug_reservation_storage(reservation_id):
    """Inspect raw saved values for reservation fields"""
    if frappe.session.user == 'Guest':
        return {'success': False, 'error': 'Not authenticated'}

    doc = frappe.get_doc('reservation', reservation_id)
    meta = frappe.get_meta('reservation')

    return {
        'success': True,
        'reservation_id': doc.name,
        'doc_total_abonado': doc.total_abonado,
        'doc_test': doc.test,
        'doc_customer_name': doc.customer_name,
        'db_total_abonado': frappe.db.get_value('reservation', doc.name, 'total_abonado'),
        'db_test': frappe.db.get_value('reservation', doc.name, 'test'),
        'db_customer_name': frappe.db.get_value('reservation', doc.name, 'customer_name'),
        'field_total_abonado_type': meta.get_field('total_abonado').fieldtype if meta.get_field('total_abonado') else None,
        'field_test_type': meta.get_field('test').fieldtype if meta.get_field('test') else None,
    }


@frappe.whitelist(allow_guest=True)
def create_customer(customer_name, telefono='', nit=''):
    """Create a new customer"""
    # Check authentication
    if frappe.session.user == 'Guest':
        return {'success': False, 'error': 'Not authenticated'}
    
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
    
    # Add phone if provided
    if telefono and telefono.strip():
        customer.custom_customer_phone = telefono.strip()
    
    # Add NIT if provided
    if nit and nit.strip():
        customer.nit_face_customer = nit.strip()
        customer.custom_nit_face_customer = nit.strip()
    
    customer.insert()
    frappe.db.commit()
    
    return {'name': customer.name, 'customer_name': customer.customer_name}

@frappe.whitelist(allow_guest=True)
def get_recent_reservations(limit=5):
    """Get the most recent reservations"""
    # Check authentication
    if frappe.session.user == 'Guest':
        return []
    
    reservations = frappe.db.sql("""
        SELECT 
            name,
            customer_name,
            habitacion,
            fecha_entrada,
            fecha_salida,
            estado_reserva,
            total_global,
            total_abonado,
            total_pendiente,
            creation
        FROM `tabreservation`
        ORDER BY creation DESC
        LIMIT %(limit)s
    """, {'limit': int(limit)}, as_dict=True)
    
    return reservations
