import os
import sys
import zlib
import base64


def clear_database():
    database_path = "config/settings.db"
    if os.path.exists(database_path):
        print("Removing previous database...")
        os.remove(database_path)
    else:
        print("Database not found")


def create_db_and_tables():
    from sqlmodel import SQLModel
    from .engine import engine

    SQLModel.metadata.create_all(engine)

# def create_settings_text():
#     config_files = os.scandir(path="config/")
#     if not "settings.txt" in config_files:
#         create_settings()

''' Load settings reader text if it doesn't exist. '''
def create_settings_text():
    comp_settings = "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"

    decoded_sett = zlib.decompress(base64.b64decode(comp_settings))

    try:
        with open("./config/settings.txt", "w") as new_settings:
            new_settings.write(decoded_sett.decode("utf-8"))
    except:
        sys.exit("Coudn't write new reader settings file")

def create_readme(self, path):
    comp_readme = "eNpVVM2O1DAMvvcpvCcuy77CCsSBkZBALBLimEndaZgmLvmhlKfns9PZXW5Nk9jfn/O0Mo/0ld349iudd/okbTyzq8PwIYy0S6Nrks0+vEuUcZCiZKY6Y1m34PWTqVgdmWzhfnN2F7bTIV365uMwfMlcClZOLwnVvFOoJK3eDcMPLnf0Lrq/uHBHp5LeVGw+DqfoLiExzUARm59795AmydHVIMmwbdKWkc5ofV6stvO/WrCDHZ6L2IvSUjWQIfIDnXQvFAJY/RmSB+CigJ33QBrOYQl113LW1KWD++iqu7e+sZWqbdHMX7WZ5JGz3khSaXLLgt054KJ+KpLEm3aSaMJUdIyld39hpOc2yWC0ZhkbsBBD0p0Ke0njwzB8bpl4x3+nuPDfaLku37IT6q8L/6HoPLrrOUCocmGUzrSFOkP2TOfsQiq0sdVZM1fQNZVHLuGSWC/BRi+XFP7ihKuVc+rlJlkWNUV+c+RUywN9mzUMSgyqIiDVmFT+U7WFZWcUNmtbaVBkt9v3Vq6IQXpmpVdFoVuhGZlSLJDl2v+sLlt2zEfIUvhX4+RRbZs53W6tK3eCo2hbCHA48KI2MhHMG+hbZdUuk/gGVxKkHcM0cQY/5BaWKlJJAF61CerqVJSqWHBPyz+bjOAyrDpVuKDWcaQlXPl5lpS6Lg7Oh/qTK7ULkhknVEyjUmZBj/8j3GOvvKK7dsVucD3y/STgWarKrhfcVYvFXTVU9zLm655ObxBMnAcOHVkFp0TUjM52FA2Yjfdtnisj9beFK68msO5r8GasbnceppQBdBgKzR9spXPTEHR6TE+vnyGYprolxepdgaMnoGiY7PH1W9PnZAoZYPCU3CF+0i4zDkNdaFKcPi9K7wjN8Qwoc0C814yvoTKMKCYpLEfMDNImRxDNbu6DcpsTHeWXWOjQw0PZsO92TMF7MDshE8EmPqRrf2W8CaQPDNTRlwqa/FQTIoa8j9DttUId7XWbkZe37Dm00OcjZs+d1SXI/0jfj3YFtTH9R7I0iFoN7A6/Hod/l9weow=="
    
    decoded_readme = zlib.decompress(base64.b64decode(comp_readme))

    with open(path+"Readme.txt", "w") as new_readme:
        new_readme.write(decoded_readme.decode("utf-8"))