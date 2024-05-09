import obd

connection = obd.OBD()

print(connection.status)

if connection.is_connected() == True:
    cmd = obd.commands.RPM
    while True:
        response = connection.query(cmd) # send the command, and parse the response
        print(response.value) # returns unit-bearing values thanks to Pint
