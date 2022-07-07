import stanfordnlp
import pandas as pd
import networkx as nx
from nltk.tree import ParentedTree

# Revisar y agregar las podas
# Saca todas las palabras como la palabra de oracion 
# Poner todos los resultados en una lista y lugo escribirlos para el archivo
 
nlp = stanfordnlp.Pipeline()

def buscar_en_lista(lista,cosa):
        j=-1
        for i in lista:
                j+=1
                if i==cosa:
                        return j
        j=-1
        return j


#Tipos de dependencia en las reglas
mod=['mod','amod','appos','advcl','det','predet','preconj',
    'vmod','mwe','mark','advmod','neg','rcmod','quantmod','nn','number',
    'prep','poss','possesive','prt']
subj=['subj','nsubj','nsubjpass', 'csubj','csubjpass']
obj=['obj','dobj' ,'iobj','pobj']

MR = ['mod','pnmod','subj' ,'s', 'obj','dobj' ,'iobj','pobj', 'obj2', 'desc','nsubj','amod','nn','num']
def dep_conjuntos(MR,senten,palabra,doc):
    edges = []
    relation=[]
    for token in senten.dependencies:
        if token[0].text.lower() != 'root':
            edges.append(token[0].text.lower())
            edges.append(token[2].text.lower())
            relation.append(token[0].dependency_relation)
            relation.append(token[2].dependency_relation)
    
    i = buscar_en_lista(edges,palabra)
    j = buscar_en_lista(MR,relation[i])
    if j!=-1:
        return True
    return False

CONJ= ['conj']

NN={'NN': 'noun, singular \'desk\'',
'NNS': 'noun plural \'desks\'' ,'NNP': 'proper noun, singular \'Harrison\'',
'NNPS': 'proper noun, plural \'Americans\'' }
       
JJ={ 'JJ': 'adjective \'big\'',
    'JJR': 'adjective, comparative \'bigger\'','JJS': 'adjective, superlative \'biggest\''}


def relacion_dependencia(O,senten):
    edges = []
    relation=[]
    for token in senten.dependencies:
        if token[0].text.lower() != 'root':
                edges.append(token[0].text.lower())
                edges.append(token[2].text.lower())
                relation.append(token[0].dependency_relation)
                relation.append(token[2].dependency_relation)
    i = buscar_en_lista(edges,O)
    return relation[i]

############################ FUNCIONES AUXILIARES PARA DEPENDENCIAS   ############################ 
def utilizando_lista(lista_interna,lista_interna_bool):
    i=-1
    for l in lista_interna:
        i+=1
        if lista_interna_bool[i]!=1:
            return i
    return -1

def buscar_root(relation):
    i=-1
    for r in relation:
        i+=1
        if r== "root":
            return i
    return -1

def encotrar_listas_internas(lista,edges):
    i = -1
    for l in lista:
        i+=1
        if l not in edges and l!=-1: #significa que l es una lista interna
            return i
    return -1


def elementos_repetidos(lista):
    list_copy = []
    i=-1
    for l in lista:
        i+=1
        if l not in list_copy or l == [] :
            list_copy.append(l)
        else:# l esta en lista
            if i+1<len(lista) and lista[i+1]==[]:
                lista[i+1]=l
    return list_copy
    


def hacer_lista(edges,relation):
    i=buscar_root(relation)
    lista = [ edges [i] ]
    listas_usadas = [ edges [i] ]
    guardar = []
    j=-1
    for e in edges:
        j+=1
        if e == edges [i]:
            guardar.append( edges [j+1] )
    
    lista.append(guardar)
    listas_usadas.append(guardar)
    k = encotrar_listas_internas(listas_usadas,edges)
    pila = []
    while(k!=-1):
        pila.append(k)
        lista_interna = listas_usadas[k]
        lista_interna_bool = []
        for lis in lista_interna:
            lista_interna_bool.append(0)

        w = utilizando_lista(lista_interna,lista_interna_bool)
        while w!=-1:
            aux = []
            j=-1
            pivote = lista_interna [ w ]
            lista_interna_bool [ w ] = 1

            for e in edges:
                j+=1
                if e == pivote and j%2==0:
                    aux.append( edges [j+1] )
            lista.append( pivote )
            lista.append ( aux )
            w = utilizando_lista(lista_interna,lista_interna_bool)
        indx=-1
        listas_usadas = []
        for elem in lista:
            indx+=1
            if indx not in pila:
                listas_usadas.append(elem)
            else:
                listas_usadas.append(-1)


        k = encotrar_listas_internas(listas_usadas,edges)

    lista = elementos_repetidos(lista)

    return lista
############################  FIN FUNCIONES AUXILIARES PARA DEPENDENCIAS   ############################ 
def dependencias(O,T,doc,entero2_3):
    #dependencia directa
    edges = []
    relation=[]
    for token in doc.sentences[0].dependencies:
        if token[0].text.lower() != 'root':
                edges.append(token[0].text.lower())
                edges.append(token[2].text.lower())
                relation.append(token[0].dependency_relation)
                relation.append(token[2].dependency_relation)
                
    lista = hacer_lista(edges,relation)
    
    i=-1
    for l in lista:
        i+=1
        #Caso1: dos palabras dependen directamente de una tercera / tres palabras involucradas
        if l not in edges and O in l and T in l and entero2_3 ==3:
            return True
        #Caso2: que una palabra dependa de otra directamente  / dos palabras involucradas
        if l not in edges and O in l and entero2_3==2:
            if lista [i-1] == T:
                return True     
        if l not in edges and T in l and entero2_3==2:
            if lista [i-1] == O:
                return True     
    
    return False

   


negacion=[ 'not', 'n’t', '’t', 'however', 'but', 'despite', 'though', 'except', 'although', 'oddly',  'aside']
#regla heterogenea
def negacion_5_palabras(T,senten):
    c=0
    L=[]
    for N in senten.words:
        if N != T and c>=0 :  #  5 palabras antes de la T
            c=c+1
            if c<=5:
                L.append(N)
            else: 
                L.pop(0)
                L.append(N)
                continue
        if N==T:
            c=-1  
            continue 
        if N!=T and c<0:
            if c>-6:
                L.append(N)
    
    for a in L:
        if a in negacion:
            return  True
    
    return False

def R11(senten,F,O_expandido,R):#extrae objetivos usando palabras de opinion
    tpos=0
    depmr=0
    dep=0
    print ("R11")
    i=0
    for T in senten.words:
        i+=1
        for O in O_expandido.keys():
            if T.text!= " "  and T.text!= ":" and T.text!= "," and T.text!= "." and T.text!= "\n" :
                print(i)
                if T.pos in NN.keys():
                    print("T.pos in NN.keys()")
                    tpos+=1
                print(T.pos in NN.keys())
                print(T.pos )
                if dep_conjuntos(MR,senten,O,R):
                    print("dep_conjuntos")
                    depmr+=1
                print(dep_conjuntos(MR,senten,O,R) )
                if dependencias(O,T.text,R,2):
                    print("def dependencias R11")
                    dep+=1
                print(dependencias(O,T.text,R,2))
                print('\n') 
                if (T.pos in NN.keys())  and (dep_conjuntos(MR,senten,O,R))  and ( dependencias(O,T.text,R,2)):
                    F[T.text]=0
                    #regla heterogenea
                    if not negacion_5_palabras(T,senten):
                        F[T.text]=O_expandido[O] #la polaridad del objetivo es heredada de la de la palabra de opinion
                    else: 
                        F[T.text]=-O_expandido[O]

    print(tpos)
    print(depmr)
    print(dep) 
    print(F)

    return F
                

def R12(senten,F_actual,O_expandido,R):#extrae objetivos usando palabras de opinion
    print ("R12")
    depmr=0
    for T in senten.words:
        for O in O_expandido.keys():
            a=O
            O=nlp(O)
            for s in O.sentences:
                for w in s.words:
                    print(T.pos in NN.keys())
                    if dep_conjuntos(MR,senten,w.text,R):
                        print("dep_conjuntos(MR,senten,w.text,R)")
                        depmr+=1
                    print (dep_conjuntos(MR,senten,w.text,R))
                    print("def dependencias R12")
                    print (dependencias(a,T.text,R,3))
                    print('\n')
                    if (T.pos in NN.keys())  and (dep_conjuntos(MR,senten,w.text,R) or dep_conjuntos(MR,senten,T.text,R)) and (dependencias(a,T.text,R,3)):
                        F_actual[T.text]=0
                        #regla heterogenea
                        if not negacion_5_palabras(T,senten):
                            F_actual[T.text]=O_expandido[a] #la polaridad del objetivo es heredada de la de la palabra de opinion
                        else: 
                            F_actual[T.text]=-O_expandido[a]
    print(depmr)
    return F_actual


def R21(senten,O_actual,F,R):#extrae palabras de opinion usando objetivos
    print ("R21")
    depmr=0
    for O in senten.words:
        for T in F.keys():
            print(O.pos in JJ.keys())
            print(O.pos)
            if dep_conjuntos(MR,senten,O.text,R):
                print("dep_conjuntos(MR,senten,O.text,R) ")
                depmr+=1
            print(dep_conjuntos(MR,senten,O.text,R) )
            print("def dependencias R21")
            print(dependencias(O.text,T,R,2))
            print('\n')
            if (O.pos in JJ.keys())  and (dep_conjuntos(MR,senten,O.text,R) ) and (dependencias(O.text,T,R,2)):
                O_actual[O.text]=0
                #regla heterogenea
                if not negacion_5_palabras(O,senten):
                    O_actual[O.text]=F[T] 
                else:
                    O_actual[O.text]=-F[T]
    print(depmr)
    
    print (O_actual)
    return O_actual


def R22(senten,O_actual,F,R):#extrae palabras de opinion usando objetivos
    print ("R22")
    for O in senten.words:
        for T in F.keys():
            print(O.pos in JJ.keys())
            print (O.pos)
            print(dep_conjuntos(MR,senten,O.text,R) )
            print("def dependencias R22")
            print(dependencias(O.text,T,R,3))
            print('\n')
            if (O.pos in JJ.keys())  and (dep_conjuntos(MR,senten,O.text,R) or dep_conjuntos(MR,senten,T,R) )  and (dependencias(O.text,T,R,3)):
                            O_actual[O.text]=0
                            #regla heterogenea
                            if not negacion_5_palabras(O,senten):
                                O_actual[O.text]=F[T] 
                            else:
                                O_actual[O.text]=-F[T]
   
    print (O_actual)
    return O_actual
################################################################################################       

#regla homogenea
def negacion_pareja_impar(Ov,On,senten):
    L=[]
    c=0
    for a in senten.words:
        if a==Ov or a==On:
            c=c+1
            continue
        if c==1:
            L.append(a)
    #cantidad de negaciones entre Ov y On
    r=0
    for n in L:
        if n in negacion:
            r=r+1
    
    if r%2==0:
        return False
    else:
        return True

        

def R31(senten,F_actual,F_extr,R):#extrae objetivos usando objetivos extraidos
    print ("R31")
    for Ti in senten.words:
        for Tj in F_extr.keys():
            print (dep_conjuntos(CONJ,senten,Ti.text,R))
            print (Ti.pos in NN)
            print("def dependencias R31")
            print (dependencias(Ti.text,Tj,R,2))
            print('\n')
            if (dep_conjuntos(CONJ,senten,Ti.text,R)) and (Ti.pos in NN) and dependencias(Ti.text,Tj,R,2):
                F_actual[Ti.text]=0
            #regla homogenea
                if not negacion_pareja_impar(F_actual,F_extr,senten):
                    F_actual[Ti.text]=F_extr[Tj]
                else:
                    F_actual[Ti.text]=-F_extr[Tj]

    return F_actual
                
def R32 (senten,F_actual,F_extr,R):#extrae objetivos usando objetivos extraidos
    print ("R32")
    for Tj in senten.words:
        for Ti in F_extr.keys():
            a=Ti
            Ti=nlp(Ti)
            Ti=Ti.sentences[0].words[0]
            print(Ti.pos ==Tj.pos )
            print(Tj.pos in NN) 
            print("def dependencias R32")
            print (dependencias(a,Tj.text,R,3))
            print('\n')
            if (Tj.pos in NN) and dependencias(a,Tj.text,R,3):
                F_actual[Tj.text]=0
                #regla homogenea
                if not negacion_pareja_impar(F_actual,F_extr,senten):
                    F_actual[Tj.text]=F_extr[a]
                else :
                    F_actual[Tj.text]=-F_extr[a]

    return F_actual
             

def R41 (senten, O_actual, O_conocida,R):#extrae palabras de opinion usando palabras de opinion extraidos
    print ("R41")
    for Oi in senten.words:
        for Oj in O_conocida.keys():
            print(dep_conjuntos(CONJ,senten,Oi.text,R)) 
            print(Oi.pos in JJ)
            print(Oi.pos)
            print("def dependencias R41")
            print(dependencias(Oi.text,Oj,R,2))
            print('\n')
            if  dep_conjuntos(CONJ,senten,Oi.text,R)  and Oi.pos in JJ and dependencias(Oi.text,Oj,R,2):
                O_actual[Oi.text]=0      
            #regla homogenea
                if not negacion_pareja_impar(O_actual,O_conocida,senten):
                    O_actual[Oi.text]=O_conocida[Oj]
                else:
                    O_actual[Oi.text]=-O_conocida[Oj]

    print(O_actual)
    return O_actual
             

def R42(senten, O_actual, O_conocida,R):#extrae palabras de opinion usando palabras de opinion extraidos
    print ("R42")
    for Oj in senten.words:
        for Oi in O_conocida.keys():
            a=Oi
            Oi=nlp(Oi)
            for s in Oi.sentences:
                for w in s.words:
                    print (relacion_dependencia(w.text,senten)==relacion_dependencia(Oj.text,senten))
                    print (Oj.pos in JJ.keys())
                    print("def dependencias R42")
                    print (dependencias(Oj.text,w.text,R,3))
                    print ('\n')
                    if Oj.text!= " "  and Oj.text!= ":" and Oj.text!= "," and Oj.text!= "." and Oj.text!= "\n" :
                        if (relacion_dependencia(w.text,senten)==relacion_dependencia(Oj.text,senten)) and (Oj.pos in JJ.keys()) and (dependencias(Oj.text,w.text,R,3)):
                            O_actual[Oj.text]=0
                            #regla homogenea
                            if not negacion_pareja_impar(O_actual,O_conocida,senten):
                                O_actual[Oj.text]=O_conocida[a]
                            else:
                                O_actual[Oj.text]=-O_conocida[a]
   
    return O_actual
###################################################################################################

#devuelve un diccionario con la palabra de opinion y su polaridad si fue extraida con objetivos de otra critica
def regla_revision_interna(O_critica, O_extraida):
    polaridad=0
    for i in O_critica.keys():
        polaridad = polaridad + O_critica[i]
    if (polaridad > 0):
        polaridad= 1
    else:
        polaridad= -1
    dic={ O_extraida:polaridad }
    return dic


def suma_dic(dic1,dic2):
        dic3=dic1
        for k in dic2.keys():
                if k not in dic3.keys():
                        dic3[k]=dic2[k]
        return dic3

def poda (senten,F):
    if len(F)>0:
        F = poda_otros_productos_distribuidores(senten,F)
    if len(F)>0:
        F = poda_global(senten,F)
    return F 
    
def incluido_dic(este,en_este):
    for a in este.keys():
        if a not in en_este.keys():
            return False
    return True

def algoritmo (O, R,archivo,objetivos_comprobar):
    O_expandido= O

    F={}
    Fi={'a':1}
    Oi={'a':1}
    while len(Fi)!=0  and  len(Oi)!=0:
        Fi={}
        Oi={}

        for senten in R.sentences:
            #extraer objetivos usando r11 y r12
                Fi=R11(senten,Fi,O_expandido,R)
                #Fi = poda(senten,Fi)
                if incluido_dic(Fi,F):
                    Fi={}
                F=suma_dic(F,Fi)
                Fi=R12(senten,Fi,O_expandido,R)
                #Fi = poda(senten,Fi)
                if incluido_dic(Fi,F):
                    Fi={}
                F=suma_dic(F,Fi)
            #extraer palabras de opinio usando r41 y r42    
                Oi=R41(senten,Oi,O_expandido,R)
                if incluido_dic(Oi,O_expandido):
                    Oi={}
                aux=O_expandido
                O_expandido = suma_dic(O_expandido,Oi)
                Oi=R42(senten,Oi,aux,R)
                if incluido_dic(Oi,O_expandido):
                    Oi={}
                O_expandido = suma_dic(O_expandido,Oi)
        Fj={}
        Oj={}

        for senten in R.sentences:
            #extraer objetivos usando r31 y r32
                    Fj=R31(senten,Fj,Fi,R)
                    if incluido_dic(Fj,Fi):
                        Fj={}    
                    #Fj = poda(senten,Fj)
                    aux = Fi
                    Fi=suma_dic(Fi,Fj)
                    F=suma_dic(F,Fj)
                    Fj=R32(senten,Fj,aux,R)
                    if incluido_dic(Fj,Fi):
                        Fj={}  
                    #Fj = poda(senten,Fj)
                    Fi=suma_dic(Fi,Fj)
                    F=suma_dic(F,Fj)
            #extraer palabras de opinio usando r21 y r22 
                    Oj=R21(senten,Oj,Fi,R)
                    if incluido_dic(Oj,Oi):
                        Oj={}  
                    Oi=suma_dic(Oi,Oj)
                    O_expandido=suma_dic(O_expandido,Oj)
                    Oj=R22(senten,Oj,Fi,R)
                    if incluido_dic(Oj,Oi):
                        Oj={} 
                    Oi=suma_dic(Oi,Oj)
                    O_expandido=suma_dic(O_expandido,Oj)

    for senten in R.sentences:
        F=suma_dic(poda(senten,F),F)
    imprimir(O_expandido,F)
    archivo = escribir_archivo(O_expandido,F,archivo)
    comp_T = prueba_T(objetivos_comprobar,F)
    comp_O = prueba_O(O,O_expandido)
    salida = [comp_T,comp_O]
    return salida
def prueba_O(O,O_expandido):
    nuevos = []
    if len(O)< len(O_expandido):
        for a in O_expandido.keys():
            if a not in O:
                nuevos.append(a)
    return nuevos
def prueba_T(objetivos_comprobar,obj_ext):
    aciertos = 0
    nuevos = []
    for t in obj_ext.keys():
        if t in objetivos_comprobar.keys():
            aciertos+=1
        else:
            nuevos.append(t)
    nuevos.append(aciertos)
    return nuevos

def escribir_archivo(O,F,archivo):
    archivo.append("{0} : {1}".format("O",len(O)))
    archivo.append("\n")
    for o in O.keys():
        archivo.append("{0} : {1}".format(o,O[o]))
        archivo.append("\n")
    archivo.append("{0} : {1}".format("F",len(F)))
    archivo.append("\n")
    for f in F.keys():
        archivo.append ("{0} : {1}".format(f,F[f]))
        archivo.append("\n")
    return archivo

def imprimir (O, F):
    print("{0} : {1}".format("O",len(O)))
    for o in O.keys():
        print("{0} : {1}".format(o,O[o]))
    print("{0} : {1}".format("F",len(F)))
    for f in F.keys():
        print ("{0} : {1}".format(f,F[f]))

def poda_objetivos_clausulas ( senten , T_extraidos):
    bandera = {}
    res_dic = {}
    for w in senten.words:
            if w=='and' or w=='or':
                bandera[senten] = True
            else: 
                bandera[senten] = False
    if bandera[senten] == False:
        suma_dic(  res_dic , aux_clausulas(senten,T_extraidos) )
    return res_dic 
    
def aux_clausulas( senten , T_extraidos):
    dic = {}
    var = ""
    for t in T_extraidos.keys():
        dic[t] = 0
    for w in senten.words:
        for t in T_extraidos.keys():
            if t == w:
                dic[t] = dic [ t ] + 1
            menor = dic [t]
            var = t

    while len( dic ) != 1:
        for t in T_extraidos.keys():
            if menor > dic[t]:
                menor = dic [t]
                var = t
        dic.pop(var)
    return dic

#indicaciones para los productos
ProductINDI = ['compare to', 'compare with', 'better than', 'worse than']       

#indicaciones para los distribuidores
DealerINDI = [ 'shop with' , 'buy from']
#elimina como objetivos los nombres de otros productores y distribuidores que se mencionan en la revision
def poda_otros_productos_distribuidores(senten, T_extraidos):
    L = []
    i = 0
    res_dic = T_extraidos
    for w in senten.words:
            if w in NN:
                L.append(w)
                i = i+1
            if  w in ProductINDI:
                if L[i] in T_extraidos.keys():
                    res_dic.pop(L[i])
                    break
    L = []
    bandera = False
    for w in senten.words:
        if w in DealerINDI:
            bandera = True
        if bandera == True and w in T_extraidos.keys():
            res_dic.pop(w)
            break
    return res_dic

def poda_frases_objetivo(senten, T_extraidos):
    #Q=2 K=1
    L = []
    frase_dic = {}
    for w in senten.words:
        if w.pos in NN:
            L.append(w)
        if w in T_extraidos.keys():
            frase_dic [w] = L[ len(L)-2: ]  #corte de lista dejando solo los dos ultimos elementos
            L = []

    bandera = False
    for w in senten.words:
        if w in T_extraidos.keys():
            bandera = True
            t=w
            continue
        if bandera == True and w.pos in JJ:
            frase_dic [t].append(t)
            frase_dic [t].append(w)
            bandera= False
    return frase_dic

def poda_global(senten, T_extraidos):
    c = {}
    for t in T_extraidos.keys():
        c[t]=0

    for w in senten.words:
            if w in T_extraidos:
                c[w]= c[w] + 1
    
    for t in T_extraidos.keys():
        if c[t] == 1:
            c.pop(t)
    res_dic = {}
    for t in c.keys():
        res_dic[t] = T_extraidos [t]
    
    return res_dic
def polaridad_revision(O):
    if len (O)!=0:
        s=0
        for x in O.keys():
            s+=O[x]
        if s>0:
            return 1
        if s<0:
            return -1

def leer (archivo_param):
    O = leer_palabras_opinion("positives.txt",1)
    O = suma_dic(O,leer_palabras_opinion("negatives.txt",0))
    archivo = []
    otro=[]
    ctdad_criticas_leidas=0
    files = open(archivo_param, "r")
    #print(texto)
    polaridad = []
    bandera=0 #inicio de una oracion con ##
    objetivos_comprobar = {}
    critica = ""
    q=0
    b=1
    it=0
    for linea in files:
        print (linea)
        if '[t]' in linea:
            if it>0:
                print("{0} {1}: {2}".format("Polariad de la revision ",it,polaridad_revision(O)) )
                it+=1
            continue
        else:
            if len(linea) > 1:
                a = nlp(linea)
                cad = ""
                i=0
                for char in a.text:
                    if i==0 and char=="#":
                        objetivos_comprobar={}
                    i+=1
                    if i==1 and char=="#":
                        bandera=1
                    if i==1 and char!="#":
                        objetivos_comprobar={}
                    if char =='[':
                        b=0
                    if  b==1:
                        if char != "#" and char != "\n" :
                            if len (objetivos_comprobar)>=1  and char != " ": 
                                cad = cad + char
                                continue
                            else:
                                cad = cad + char
                                continue
                    if (char == '[' or char == '+' or char == '-' or char == '1' or char == '2' or char == '3' or char == ']') and bandera == 0:
                        polaridad.append (char)
                        continue
                    if len(polaridad) == 4:
                        objetivos_comprobar=suma_dic(objetivos_comprobar,procesar(polaridad,cad))
                        polaridad = []
                        b=1
                        cad = ""
                        continue
                    if char == '#' and bandera == 0:
                        bandera = 1
                        continue
                    if bandera == 1 and char != '#' and char!= "\n" :
                        cad += char
                        continue
                    
                    if char == '\n':
                        q=1                
                    if q==1:
                        critica = nlp(cad)
                        ctdad_criticas_leidas+=1
                        archivo.append("\n \n \n Critica No.: ")
                        archivo.append(str(ctdad_criticas_leidas))
                        archivo.append("\n")
                        otro.append(algoritmo (O,critica,archivo,objetivos_comprobar))
                        critica = ""
                        cad = ''
                        q=0
                        b=1
                        bandera=0
    """ resultados = open("resultados.txt", "w")
    for w in archivo:
        if w!= "\n":
            resultados.write(w)
        resultados.write("\n")"""
    files.close() 
    res = open("resultados.txt", "w")
    for w in otro:
        res.write(str(w))
        res.write("\n")
    res.close()


def comprobaciones(objetivos_comprobar,F,O,O_ext):
    aciertos_obj = 0
    obj_nuevos = {}
    for k in F.keys():
        if k in objetivos_comprobar.keys():
            aciertos_obj+=1
        else:
            obj_nuevos[k]=F[k]
    O_nuevas = {}
    for k in O_ext.keys():
        if k not in O.keys():
            O_nuevas[k] = O_ext[k]
                


def procesar(polaridad,nuevo):
    O ={}
    if polaridad == ['[','+','1',']']:
        O[nuevo]=1
        return O 
    if polaridad == ['[','+','2',']']:
        O[nuevo]=2  
        return O   
    if polaridad == ['[','+','3',']']:
        O[nuevo]=3  
        return O     
    if polaridad == ['[','-','3',']']:
        O[nuevo]=-3 
        return O   
    if polaridad == ['[','-','2',']']:
        O[nuevo]=-2
        return O 
    if polaridad == ['[','-','1',']']:
        O[nuevo]=-1
        return O 
def leer_palabras_opinion (archivo,pos):
    files = open(archivo, "r")
    O={}
    for linea in files:
        palabra = ""
        for char in linea:
            if char!="\n":
                palabra+=char
            if char=="\n":
                if pos==1:
                    O[palabra]=1
                else:
                    O[palabra]=-1
    files.closed
    return O




leer("prueba.txt")
