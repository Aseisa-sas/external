# ADRES Consultation API

This is a **FastAPI** project that provides a JSON endpoint to consult Colombian health entity affiliation data (EPS) from the **ADRES** website. It uses **Selenium** and **Undetected Chromedriver** to bypass bot protections and scrape the data in real-time.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your machine:

1.  **Python 3.10** or higher.
2.  **Google Chrome** browser (latest version recommended).
    *   *Note: You do not need to manually download `chromedriver`; the script handles this automatically.*

---

## 🛠️ Installation & Setup

Follow these steps to set up the project locally.

### 1. Create the Project Folder
If you haven't already, create a folder for the project and enter it:

```bash
git clone git@github.com:Aseisa-sas/external.git
cd external
```

### 2. Set up the Virtual Environment (venv)

It is highly recommended to use a virtual environment to manage dependencies.

**🟢 Linux / macOS:**
```bash
# Create the virtual environment
python3 -m venv venv

# Activate the environment
source venv/bin/activate
```

**🔵 Windows (PowerShell):**
```powershell
# Create the virtual environment
python -m venv venv

# Activate the environment
.\venv\Scripts\activate
```

*(You will know it is active because you will see `(venv)` at the start of your command line).*

### 3. Install Dependencies

With the virtual environment active, install the required packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Server

To start the server, use **Uvicorn**. Run the following command from the root folder (`adres_api/`):

```bash
uvicorn app.main:app --reload
```

*   `app.main:app`: Refers to the `app` instance inside `app/main.py`.
*   `--reload`: Makes the server restart automatically if you change code (useful for development).

You should see output similar to:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 📡 API Usage

### 1. Consult an Identity
**Endpoint:** `GET /consult/{identity}`

**Example URL:**
http://127.0.0.1:8000/consult/27355199

**Response (JSON):**
```json
{
  "type_identity": "CC",
  "identity": "27355199",
  "names": "MARIA ELENA",
  "last_names": "PEREZ LOPEZ",
  "birthday": "**/**/**",
  "province": "BOGOTA",
  "municipality": "BOGOTA",
  "status": "ACTIVO",
  "entity": "EPS SANITAS",
  "regime": "CONTRIBUTIVO",
  "effective_date_membership": "01/01/2020",
  "end_date_membership": "-",
  "type_member": "COTIZANTE"
}
```

### 2. Interactive Documentation (Swagger UI)
FastAPI provides automatic documentation. Open your browser and go to:

http://127.0.0.1:8000/docs

Here you can test the API directly from the browser.

---

## 📂 Project Structure

Your project folder should look like this:

```text
adres_api/
├── venv/                   # Virtual environment folder
├── requirements.txt        # List of python dependencies
├── README.md               # This file
└── app/
    ├── __init__.py         # Makes 'app' a package
    ├── main.py             # FastAPI entry point & Routes
    ├── models.py           # Pydantic JSON schemas
    └── scraper.py          # Selenium logic to extract data
```

---

## ⚠️ Important Notes

1.  **Browser Window**: When you request data, a Chrome window will open automatically. **Do not close or minimize it instantly**, as the script needs it to render the ADRES results popup. It will close automatically once the data is extracted.
2.  **Performance**: Since this uses a real browser (Selenium), requests may take 5-15 seconds depending on the ADRES website speed and your internet connection.
3.  **Linux Servers**: If you deploy this on a Linux server (like Ubuntu Server) with no monitor, you must install `Xvfb` (virtual display) to allow Chrome to run.
