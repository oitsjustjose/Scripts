@rem For use with Lenovo Legion laptops when the Audio driver outright dies from sleep or hardware change????
pnputil /disable-device "SWD\DRIVERENUM\{C3A63EDD-2D27-4B66-B155-5E94B43D926A}#REALTEKAPO&6&1DC6BD64&0"
pnputil /enable-device "SWD\DRIVERENUM\{C3A63EDD-2D27-4B66-B155-5E94B43D926A}#REALTEKAPO&6&1DC6BD64&0"