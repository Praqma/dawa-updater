from models import *

def main():
    for a in SamAreatype.select():
        print(a.areatypeid)

    database.close()

if __name__ == '__main__':
    main()
