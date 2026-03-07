import frappe
import os
from datetime import datetime, timedelta

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
    
    if not start_date:
        start_date = get_monday(datetime.now().date())
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
        
        # Initialize all days as free
        current_date = start_date
        for i in range(8):
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
    
    # Calculate totals per day
    totals = {}
    current_date = start_date
    for i in range(8):
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
    """Generate week information for header"""
    days = []
    day_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    current_date = start_date
    today = datetime.now().date()
    
    for i in range(8):
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
