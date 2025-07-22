#!/usr/bin/env python3

import os
import time
import requests
import pytz
import argparse
from datetime import datetime
from flask import Flask, jsonify
import json

def load_config(config_file='config.txt'):
    """
    Load configuration from file.
    Returns list of dictionaries with keys: departure, destination, bus_number
    """
    routes = []
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse line: departure|destination|bus_number
                parts = line.split('|')
                if len(parts) != 3:
                    print(f"⚠️  Warning: Invalid format on line {line_num}: {line}")
                    continue
                
                departure, destination, bus_number = parts
                routes.append({
                    'departure': departure.strip(),
                    'destination': destination.strip(),
                    'bus_number': bus_number.strip()
                })
        
        print(f"✅ Loaded {len(routes)} routes from {config_file}")
        return routes
        
    except FileNotFoundError:
        print(f"❌ Configuration file '{config_file}' not found!")
        return []
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return []

def get_bus_departures(stop_name, bus_number, destination, limit=100, hours_ahead=2):
    """
    Get bus departures for a specific route from OpenData.ch API.
    """
    try:
        # Build the API URL with specific bus number and destination
        url = f"http://transport.opendata.ch/v1/stationboard"
        params = {
            'station': stop_name,
            'limit': limit,
            'transportations': 'bus'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        departures = []
        
        for connection in data.get('stationboard', []):
            connection_bus = connection.get('number')
            connection_to = connection.get('to', '')
            
            # Check if this is the bus we're looking for
            if (connection_bus == str(bus_number) and 
                destination in connection_to):
                
                departure_time = connection.get('stop', {}).get('departure')
                if departure_time:
                    try:
                        # Fix timezone format if needed
                        if '+0200' in departure_time:
                            departure_time = departure_time.replace('+0200', '+02:00')
                        elif '-0200' in departure_time:
                            departure_time = departure_time.replace('-0200', '-02:00')
                        
                        # Parse departure time
                        dt = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
                        swiss_tz = pytz.timezone('Europe/Zurich')
                        dt = dt.astimezone(swiss_tz)
                        
                        # Only include departures in the future (within specified hours)
                        now = datetime.now(swiss_tz)
                        if dt > now and (dt - now).total_seconds() < (hours_ahead * 3600):
                            # Get delay information
                            delay = connection.get('stop', {}).get('delay')
                            platform = connection.get('stop', {}).get('platform', 'N/A')
                            
                            departures.append({
                                'time': format_departure_time(departure_time),
                                'from': stop_name,
                                'to': connection_to,
                                'bus': bus_number,
                                'delay': format_delay(delay) if delay is not None else "🟢 On time",
                                'platform': platform,
                                'departure_timestamp': dt.isoformat()
                            })
                    except Exception as e:
                        print(f"⚠️  Error parsing time '{departure_time}': {e}")
                        continue
        
        return departures
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {stop_name}: {e}")
        return []
    except Exception as e:
        print(f"Error for {stop_name}: {e}")
        return []

def format_departure_time(departure_str):
    """
    Format departure time string to readable format.
    """
    try:
        # Handle different time formats
        if 'T' in departure_str:
            # Extract time part from ISO format
            time_part = departure_str.split('T')[1]
            if '+' in time_part:
                time_part = time_part.split('+')[0]
            return time_part[:5]  # HH:MM
        else:
            return departure_str
    except:
        return departure_str

def format_delay(delay_seconds):
    """
    Format delay information for display.
    """
    if delay_seconds is None:
        return "🟢 On time"
    elif delay_seconds == 0:
        return "🟢 On time"
    elif delay_seconds > 0:
        if delay_seconds < 60:
            return f"🟡 +{delay_seconds}s"
        else:
            minutes = delay_seconds // 60
            seconds = delay_seconds % 60
            if seconds == 0:
                return f"🟡 +{minutes}min"
            else:
                return f"🟡 +{minutes}min {seconds}s"
    else:
        # Negative delay means early
        abs_delay = abs(delay_seconds)
        if abs_delay < 60:
            return f"🟢 -{abs_delay}s"
        else:
            minutes = abs_delay // 60
            seconds = abs_delay % 60
            if seconds == 0:
                return f"🟢 -{minutes}min"
            else:
                return f"🟢 -{minutes}min {seconds}s"

# Flask app setup
app = Flask(__name__)

# Global variables
routes = []
hours_ahead = 2

@app.route('/api/status')
def status():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(pytz.timezone('Europe/Zurich')).isoformat(),
        'routes_loaded': len(routes),
        'hours_ahead': hours_ahead
    })

@app.route('/api/bus_departures')
def bus_departures():
    """Get all bus departures for configured routes."""
    try:
        all_departures = []
        
        for route in routes:
            departures = get_bus_departures(
                route['departure'], 
                route['bus_number'], 
                route['destination'], 
                limit=50,
                hours_ahead=hours_ahead
            )
            all_departures.extend(departures)
        
        # Sort by departure time
        all_departures.sort(key=lambda x: x.get('departure_timestamp', ''))
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now(pytz.timezone('Europe/Zurich')).isoformat(),
            'total_departures': len(all_departures),
            'hours_ahead': hours_ahead,
            'departures': all_departures
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now(pytz.timezone('Europe/Zurich')).isoformat()
        }), 500

@app.route('/api/routes')
def get_routes():
    """Get configured routes."""
    return jsonify({
        'status': 'ok',
        'routes': routes,
        'total_routes': len(routes)
    })

def main():
    """Main function to start the API server."""
    global routes, hours_ahead
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Luzern Bus Monitor API Server')
    parser.add_argument('--config', default='config.txt',
                       help='Configuration file path (default: config.txt)')
    parser.add_argument('--hours', type=int, default=2,
                       help='Hours into the future to look for departures (default: 2)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to run the server on (default: 5000)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind to (default: 0.0.0.0)')
    args = parser.parse_args()
    
    print("🚌 Luzern Bus Monitor API Server")
    print("="*50)
    
    # Load configuration
    routes = load_config(args.config)
    if not routes:
        print("❌ No routes configured. Please check your config.txt file.")
        return
    
    hours_ahead = args.hours
    
    print(f"📁 Config file: {args.config}")
    print(f"⏰ Time window: {hours_ahead} hours ahead")
    print(f"🚌 Monitoring {len(routes)} routes:")
    for route in routes:
        print(f"   Bus {route['bus_number']}: {route['departure']} → {route['destination']}")
    
    print(f"🌐 Starting API server on {args.host}:{args.port}")
    print("🌐 API Endpoints:")
    print("   - GET /api/status - Health check")
    print("   - GET /api/bus_departures - Get departure data")
    print("   - GET /api/routes - Get configured routes")
    print("="*50)
    
    # Start Flask server
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main() 