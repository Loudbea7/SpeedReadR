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
    import sqlite3

    create_path("./config")
    # Path("./config").mkdir(parents=True, exist_ok=True)

    config_path = os.listdir(os.path.join("./config", ''))

    if not "settings.db" in config_path:
        try:
            sqlite3.connect("./config/settings.db")
        except:
            print("Can't create database")

    SQLModel.metadata.create_all(engine)

def create_path(new_path):
    from pathlib import Path
    Path(new_path).mkdir(parents=True, exist_ok=True)
    # Path("./Books").mkdir(parents=True, exist_ok=True)


''' Load settings reader text if it doesn't exist. '''
def create_settings_text():
    comp_settings = "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"

    decoded_sett = zlib.decompress(base64.b64decode(comp_settings))

    try:
        with open("./config/settings.txt", "w") as new_settings:
            new_settings.write(decoded_sett.decode("utf-8"))
    except:
        sys.exit("Coudn't write new reader settings file")

def create_readme(path):
    comp_readme = "eNptVsuO3DYQvOsruHPxIeN1gtz24geMIAPEiOF1YPjIkSgNdyRS5sOz8tenqilqdhPfJD76UV1dzfvZmE59Mrp7+UkdF/WXz93R6NQ0zXvbqcVndXb+Ih+tdirgpJp8MCqd8JsutuWnUVEM+V5+9HcT9GDktHVD2XzdNB+DiRF/mpe8SmFRNimf003TfDXxRr2d9A9cuFGH6F4kbL5uDpMerDPqhCim3J6Kd+t6HyadrHcS28XnsVNHuD6OYlu337KVgyU8PWFv8tklCdJO5lYduGejQrBctK5FwJEB67ZFpPZoR5sWmhOn2q25dzrpvfidckx0C2ftmc586EzgDeeT6vU4YvdkcZGfjMSZCz35SYBJ8DjF4v2aEc9dfEBGc/BdRizKANJFRdN61902zd85KLNgXTMurEtausA3Lgr259E8qkm38M5zCCH5wcB0UBebToA9qGPQ1kV1MWJnDiYhXUG5M9EOzvASytj6wdkfOKFTMsEVc70fRxbFfzeTcSneqs8nkoGJAVUQJEkmyTwmuhDudN5IaXPMQGSR23sxF72EtGXFq56hi6ETOMVYAMu5rMw6CHekjoAlmm/ZuBbWLifj6q15NiXBztMtAFgrcEUbnLBSG+Cb/EwvvW8zquIAbWf73gTkB96ipIzUOwSe6AR22RUxMRbco/mtyCCuQakOCVVg6cykRns2Wy8xdf6sOa/o9zqmAkgwOEEwJZV48vDxnMKF9sxr0ueCWA23Bb/vPfKMibDzgj7T2LQQQ1YvoL/26vACxMR5xMGWZXBMhMUo2XaeBJP2rv2cDFhff3R80oFpmW0rheV2yUOQkgA1moL8Q1nVMZMEJT2j7p/qEIoG3D54OAH/j2jppcgNewq+XkhXba0+gMNgz1RFiOxm8OyBgD4TJ/JjEElkydFNTq2N1tsAR9Ai8tfn4aQOLA9AjZr6RG8r61YdIXTIcc8mmW0yqGSUmoAz4KnkdPErk4UvpnRabTRqwZVXVA2QwF+wrxe00TsEfwCprEiGdeciU60gTIUCHswfoD6wikyz9GCVO9ihr9pkVzHcWA+A/0Tz6iORAqav1ZfVXYTtlmgKNclkWkN2a8Gh4weo8Vy4MliQGCKuiSAEHOmy6ZZ6+ka9eTJT/ong2F3T3JPMbU7xrkHpMQ7u1Dzq5dWsczRYuqtiXGv6y2+/qi8fPzTq/R1Qf7b1sm79cUeFG0CKPo9jxCHjmoaatHv1zvtz3Ek1dq8gFr0ddigBlC35YKuO5uSJTiEwnSTSifRlqiEXcAs9N5sidWg80+s8UpagrT14x4urjP2X3WuzRKoAyST3ITkio+JrzqwlWjjPM6DC7d6OVRgf0bYTmiukfq/MnI97NXf4hInHPeX2Vn1dNaZF2wwliGtg8gfK2G61q8zjPGKwhdoTCCQr20so1Czk+7aH8jOuRH4LN44EoFIO06Cro0V2nxuuohdxAOOF0x+XigXxVhRv9Lq77pzM2PMotJOLU1Hk0VIhaybhKqgzZ7A03CztbUo0Yg5x+63lgx1OiXPCIpSL8F6fN+2TE6gVoi4kQvY/w9NHK/NjffS0OUS/AoCx4TPlqR0ZE8N2Sz1I+RW5jyg3H03upy4/19G51QxTnuCvgPHh8piCboUd9cyuHroFTXbVdmF8KQkBYtdGRmnMDJ+skna6ZlOfKn12Lddw8ru2I/X2f8xC64scrsouAfu+MADMkbdA4dFFO5mRunvgo+lZQlWyq3r6p0CvwJQXkLzcBJxQtPR3FUefhIalnhvTdB2vmxs+5GQOre+1QsYV611ZYwY7QuAvsTJixkw2ZcQ8rwjKOx+9DvJMEoeUwlhOadHCssYc5CFZngp1dm78XHkC7FeqVgKA9eZacEItyNS52WkMpsl3Zn1CTaw1Ok5hbKT1mWYd9Wy/AdMFPHJKi0KWjpqOg/RYeeXKSJjW5y4eJDlleRz6B6jl1u8jMJG4ODa1O8enSv8vx4RgZw=="
    
    decoded_readme = zlib.decompress(base64.b64decode(comp_readme))

    with open(os.path.join(path, "Readme.txt"), "w") as new_readme:
        new_readme.write(decoded_readme.decode("utf-8"))