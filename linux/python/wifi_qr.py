import argparse
import dep_mgr

try:
    import qrcode
except ImportError:
    dep_mgr.install_package("qrcode[pil]")
finally:
    import qrcode


def main(args):
    img = qrcode.make(f"WIFI:S:{args.ssid};T:WPA;P:{args.passwd};;")
    img.save(args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="WiFi QR Generator", description="Creates QR Codes to join a Password Protected WiFi Network")
    parser.add_argument("ssid", help="The SSID of the WiFi Network to connect to")
    parser.add_argument("passwd", help="The passphrase of the WiFi Network to connect to")
    parser.add_argument("-o", "--output", required=True, help="Where to save the resulting image to")
    args = parser.parse_args()
    main(args)
