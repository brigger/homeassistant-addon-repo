# 🚌 Luzern Bus Monitor - Home Assistant Add-on

A custom Home Assistant add-on that provides a RESTful API server for monitoring Luzern bus departures.

## 📋 Features

- Real-time bus departure monitoring
- RESTful API endpoints
- Configurable routes and time windows
- Easy Home Assistant integration
- Automatic startup and management

## 🏠 Installation

### Option 1: Add Repository (Recommended)

1. Go to **Settings** → **Add-ons** in Home Assistant
2. Click the three dots (⋮) → **Repositories**
3. Add: `https://github.com/your-username/homeassistant-addon-repo`
4. Click "Add"
5. Search for "Luzern Bus Monitor"
6. Click "Install"

### Option 2: Local Installation

1. Copy the `luzern_bus_monitor` folder to `/config/addons/local/`
2. Restart Home Assistant
3. The add-on will appear in the Add-ons list

## 🔧 Configuration

The add-on can be configured through the Home Assistant UI:

- `hours_ahead`: Hours into future to look for departures (default: 2)
- `scan_interval`: How often to update in seconds (default: 30)

## 📊 API Endpoints

- `GET /api/status` - Health check
- `GET /api/bus_departures` - Get departure data
- `GET /api/routes` - Get configured routes

## 🎯 Home Assistant Integration

After installing the add-on, configure Home Assistant sensors using the provided configuration files.

## 📝 License

MIT License
