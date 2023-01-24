import xml.etree.ElementTree as ET
import shutil

#Array que contiene los nombres de las redes que se encuentran en el fichero.
netsNames=[]
for i in range(65,91):
    for j in range(65,91):
        netsNames.append(chr(i)+chr(j))

#Variables necesarias para leer el xml especificado
name ="abilene.xml" #Nombre del fichero ---> Si se quiere cambiar de fichero hay que cambiar este nombre
tree = ET.parse("xml/"+name)
root = tree.getroot()
ns = {'ns': 'http://sndlib.zib.de/network'}


#Obtenemos los nodos de la red
totalNodes = [] #variable que almacena los nodos de la red

for node in root.find('.//ns:networkStructure', ns).findall('.//ns:node', ns):
    totalNodes.append({"nombre" : node.attrib['id'], "interfaces": 0, "redes" : []})

print()
print("Total nodos -> " + str(len(root.find('.//ns:networkStructure', ns).findall('.//ns:node', ns))))

#Obtenemos los enlaces de la red
totalLinks = [] #variable que almacena los enlaces de la red
netLetter = 0 #variable auxiliar para asignar un nombre a cada enlace
nets=[] #Diccionario que almacena la red con su nombre e ips de los nodos

ipNetNumber = 0
for link in root.find('.//ns:networkStructure', ns).findall('.//ns:link', ns):
    newNet = True
    for net in nets:
        if link.find('.//ns:source', ns).text == net['target'] and link.find('.//ns:target', ns).text == net['source']:
            newNet=False
            break
    if newNet:
        nets.append({"netname": netsNames[netLetter],
                                    "ip": "10.0."+str(ipNetNumber)+".0",
                                    "source":link.find('.//ns:source', ns).text,
                                    "target":link.find('.//ns:target', ns).text,
                                    "sourceip": "10.0."+str(ipNetNumber)+".1",
                                    "targetip": "10.0."+str(ipNetNumber)+".2"})
        netLetter +=1
        ipNetNumber +=1

print()
print("Total enlaces -> " + str(len(nets)))
print()

#Se definen las redes para cada nodo
for node in totalNodes:
        for net in nets:
            if node['nombre'] in net['source']:
                node['redes'].append({"nombre" : net['netname'], "interface": str(node['interfaces']), "ip": net['sourceip']})
                node['interfaces'] += 1

            if node['nombre'] in net['target']:
                node['redes'].append({"nombre" : net['netname'], "interface": str(node['interfaces']), "ip": net['targetip']})
                node['interfaces'] += 1    

#Comprobamos si existe el directiorio de la red dentro del laboratorio, si no existe lo creamos
import os
if not os.path.exists('laboratorio/'+name.split('.')[0]):
    os.makedirs('laboratorio/'+name.split('.')[0])

#escribimos fichero .conf y los ficheros startup
with open('laboratorio/'+name.split('.')[0]+"/lab.conf", 'w') as f:
    for node in totalNodes:
        for red in node['redes']:
            f.write(node['nombre'].lower().replace('.','')+"["+red['interface']+']=\''+red['nombre']+"\'\n")
        with open('laboratorio/'+name.split('.')[0]+"/"+node['nombre'].lower().replace('.','')+'.startup', 'a') as f1:
            for red in node['redes']:
                f1.write("ifconfig eth"+str(red['interface'])+ " "+ red['ip']+ "/24 up\n")

            f1.write("\n/etc/init.d/quagga start\n")
            f1.close()
        f.write('\n')
f.close()

#escribimos ficheros starups y copiamos la configuracion rip para cada nodo  
for node in totalNodes:
    shutil.copytree('rip config', 'laboratorio/'+name.split('.')[0]+'/'+ node['nombre'].lower().replace('.','').replace('.',''))