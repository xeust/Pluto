"""

    printCups is a module that prints a given file using cups

"""
import cups

"""

    executePrint() opens a cups connection, selects the first printer and prints
    a desired file to this printer

    Args:
        fileName: String with address of the file for printing

"""
def executePrint(fileName):
    conn = cups.Connection()
    printers = conn.getPrinters()
    printerName = printers.keys()[0]
    conn.printFile(printerName, fileName, "Python_Status_print", {})
    return

def main():
    return

if __name__== "__main__":
    main()
