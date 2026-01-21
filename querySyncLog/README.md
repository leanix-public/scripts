# LeanIX Synchronization Items Query Tool

A Python script to query and export LeanIX Synchronization Items with filtering, Excel export, and streaming capabilities.

## 📋 Prerequisites

- **Python 3.8 or higher**
- **LeanIX API Token** (Technical User recommended)
- **LeanIX Workspace Access**

## 🚀 Quick Setup

### 1. Clone or Download the Script

Download the following files to your working directory:
- `query_sync_items_with_status.py`
- `requirements.txt`
- `README.md` (this file)

### 2. Set Up Python Environment

**Option A: Using Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv leanix-sync-env

# Activate virtual environment
# On Windows:
leanix-sync-env\Scripts\activate
# On macOS/Linux:
source leanix-sync-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Global Installation**
```bash
# Install dependencies globally
pip install -r requirements.txt
```

### 3. Get Your LeanIX API Token

1. **Log into your LeanIX instance**
2. **Go to Administration → Technical Users**
3. **Create or use an existing Technical User**
4. **Copy the API Token**

### 4. Region Configuration (Optional)

The script defaults to region/sub-domain `enbridgeca` which works for Enbridge specific LeanIX instances. **You typically don't need to specify the region.**

Only specify the region if you get authentication errors or are using a different LeanIX sub-domain. Your LeanIX region/sub-domain can be found in your URL:
- `https://enbridgeca.leanix.net` → region: `enbridgeca` (default)
- `https://demo-eu-2.leanix.net` → region: `demo-eu-2`
- `https://us-1.leanix.net` → region: `us-1`  
- `https://eu-1.leanix.net` → region: `eu-1`
- `https://app.leanix.net` → region: `eu`

## 📖 Usage

### Basic Usage

```bash
# Get all sync items (last 30 days, auto-exported to Excel)
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN

# Get ERROR items only
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN --status ERROR

# Custom date range
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN \
  --start-date 2024-01-01 --end-date 2024-01-31

# Custom Excel filename
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN \
  --status ERROR --excel error_report.xlsx
```

### Advanced Usage

```bash
# JSON export instead of Excel
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN \
  --status OK --output success_items.json

# Stream large datasets (memory efficient)
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN \
  --stream --excel large_dataset.xlsx

# Limit number of items
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN \
  --limit 100

# Debug mode for troubleshooting
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN \
  --debug --status ERROR

# Verbose output (show sample items)
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN \
  --verbose --limit 10
```

### Using Environment Variables

Set environment variables to avoid passing tokens in command line:

**Windows:**
```cmd
set LEANIX_API_TOKEN=your_api_token_here
set LEANIX_WORKSPACE_ID=your_workspace_id_here
python query_sync_items_with_status.py --status ERROR
```

**macOS/Linux:**
```bash
export LEANIX_API_TOKEN="your_api_token_here"
export LEANIX_WORKSPACE_ID="your_workspace_id_here"
python query_sync_items_with_status.py --status ERROR
```

## 📊 Output Formats

### Default Excel Export
- **Main Sheet**: All sync items with formatted columns
- **Summary Sheet**: Statistics breakdown by status, type, and source
- **Auto-formatting**: Color-coded status, proper date formatting, auto-sized columns

### JSON Export
- Structured JSON with metadata
- Timestamp and filter information
- Raw API response data preserved

## 🎯 Available Filters

### Status Values
- `OK` - Successful synchronization
- `WARNING` - Completed with warnings
- `ERROR` - Failed synchronization
- `INFO` - Informational messages

### Date Filtering
- `--start-date`: Start date (YYYY-MM-DD or ISO format)
- `--end-date`: End date (YYYY-MM-DD or ISO format)
- **Default**: Last 30 days if no dates specified

### Other Filters
- `--limit`: Maximum number of items to retrieve
- `--batch-size`: Items per API request (default: 100)

## ⚡ Performance Options

### Streaming Mode (`--stream`)
Use for large datasets to avoid memory issues:
```bash
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN --stream
```

**When to use streaming:**
- Expecting > 1,000 sync items
- Limited system memory
- Want to process data incrementally

### Batch Size Tuning
```bash
# Larger batches (faster, more memory)
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN --batch-size 200

# Smaller batches (slower, less memory)
python query_sync_items_with_status.py --api-token YOUR_API_TOKEN --batch-size 50
```

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# If using virtual environment, make sure it's activated
source leanix-sync-env/bin/activate  # macOS/Linux
# or
leanix-sync-env\Scripts\activate     # Windows
```

**2. Authentication Errors**
```bash
# Check your API token and region
python query_sync_items_with_status.py --api-token YOUR_TOKEN --region YOUR_REGION --debug
```

**3. No Data Returned**
```bash
# Check date range (default is last 30 days)
python query_sync_items_with_status.py --api-token YOUR_TOKEN --start-date 2024-01-01 --verbose
```

**4. Excel Export Issues**
```bash
# Install Excel support
pip install openpyxl

# Use JSON export as fallback
python query_sync_items_with_status.py --api-token YOUR_TOKEN --output data.json
```

### Debug Mode
Enable detailed logging:
```bash
python query_sync_items_with_status.py --api-token YOUR_TOKEN --debug
```

### Getting Help
```bash
# Show all available options
python query_sync_items_with_status.py --help
```

## 📁 File Structure

After running, you'll typically see:
```
your-directory/
├── query_sync_items_with_status.py
├── requirements.txt
├── README.md
└── leanix_sync_items_all_20240108_143000.xlsx  # Generated output
```

## 🔐 Security Notes

- **Never commit API tokens** to version control
- **Use environment variables** for tokens in production
- **API tokens are masked** in logs for security
- **Use `--debug` sparingly** as it may expose sensitive data

## 📝 Example Outputs

### Console Output
```
================================================================================
LeanIX Synchronization Items Query
================================================================================
Region: demo-eu-2
Workspace ID: 7067cg83-8dvc-4w2f-8d3b-75b6a5e46d26
Batch size: 100
Status filter: ERROR
Start date: 2024-01-08T07:38:42-06:00 (default: last 30 days)
End date: 2024-01-08T13:38:42-06:00 (default: current time)
================================================================================

📄 Fetching page 1...
✓ Successfully retrieved sync items (page size: 25)
   Retrieved 25 items, 15 match date range (total: 15)

================================================================================
SYNC ITEMS SUMMARY
Filter: status = ERROR
================================================================================
Total items: 15

Items by status:
  ERROR: 15

Items by source:
  API_INTEGRATION: 8
  FILE_IMPORT: 7

📊 Saved 15 items to Excel file: leanix_sync_items_error_20240108_143000.xlsx
   Worksheets: 'Sync Items' (data) and 'Summary' (statistics)

✓ Query completed successfully
```

## 🤝 Support

For issues or questions:
1. Check this README for common solutions
2. Use `--debug` flag for detailed error information
3. Review the LeanIX API documentation
4. Contact your LeanIX administrator for API access issues

---
**Happy querying! 📊✨**
