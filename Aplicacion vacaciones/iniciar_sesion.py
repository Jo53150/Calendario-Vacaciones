# USUARIO Y CONTRASEÑA
datos = ["usuario1","12345"]


#PEDIR USUARIO Y CONTRASEÑA

print("USUARIO Y CONTRASEÑA")
usuariot = input("USUARIO: ")

contraseñat = input("CONTRASEÑA: ")

if usuariot and contraseñat in datos:
    print("Bienvenido Usuario1")
else :
    print("Usuario o contraseña incorrectos")
    

