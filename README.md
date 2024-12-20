## Environment Setup

### Create a Virtual Environment

1. Install `virtualenv`:
   ```bash
   pip install virtualenv
   ```

2. Create a virtual environment:
   ```bash
   virtualenv env
   ```

### Activate the Virtual Environment

#### Windows:
```bash
.\env\Scripts\activate.bat
```

#### Mac/Linux:
```bash
source ./env/Scripts/activate
```

## Install Requirements

After activating the virtual environment, install the necessary dependencies:
```bash
pip install -r requirements.txt
```

## Run the Program

Start the application:
```bash
python main.py
```
