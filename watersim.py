import numpy as np
import tcod
#VERSAO SEM PRESSAO. PRONTA.
W = 10
H = 10
LENGTH = 50
MAXVOLUME = 1
PADDING = ((1,1),(1,1))
water = []         
water.append(np.pad(np.zeros((W,H),np.longdouble),PADDING))
water[0][2:9,2:4] = 1
free = []
free.append(np.pad(np.full((W, H),-1,np.int8),PADDING))
free[0][:,10] = 0
free[0][1,:] = 0
free[0][10,:] = 0
free[0][3:6,4] = 0
free[0][2:8,6] = 0
console = tcod.Console(W, H, order="F")
tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD,
    )
def printarray(i):
    xpad,ypad = PADDING
    x0,_ = xpad
    y0,_ = ypad
    for y in range(y0,y0+H):
        for x in range(x0,x0+W):
            value = int(255*water[i][x,y])
            groundvalue = free[i][x,y]+1
            if groundvalue==1:
                groundvalue = 100
            console.print(x-x0,y-y0,str(groundvalue-1),(100+100*(value==0),100-100*(value==0),100-100*(value==0)),(min(255,10*value),min(255,20*value),min(255,20*value)))
            #except:
                #print(x,y,value)

#fluid sim
def downdemand(paddedwater,freearray,x,y):#Quanta agua falta ao de baixo pra encher
    return (freearray[x,y+1]!=0)*(MAXVOLUME - paddedwater[x,y+1])#Se o de baixo nao for parede, ele demanda o que falta pra encher
def notdown(paddedwater,freearray,x,y):
    return max(0,paddedwater[x,y] - downdemand(paddedwater,freearray,x,y))#Tirando o que o de baixo demanda, sobra isso
def update(paddedwater,freearray):
    newarray = np.pad(np.zeros((W,H),np.longdouble),PADDING)
    xpad,ypad = PADDING
    x0,_ = xpad
    y0,_ = ypad
    for y in range(y0,y0+H):
        for x in range(x0,x0+W):
            newarray[x,y] = (freearray[x,y]!=0)*(notdown(paddedwater,freearray,x,y)+min(downdemand(paddedwater,freearray,x,y-1),paddedwater[x,y-1]))
    newarray2 = np.pad(np.zeros((W,H),np.longdouble),PADDING)
    newfree = np.pad(np.full((W,H),-1,np.int8),PADDING)
    for y in range(y0,y0+H):
        for x in range(x0,x0+W):
            if freearray[x,y]==0:
                newarray2[x,y] = 0
                newfree[x,y] = 0
            else:
                watersum = np.sum(newarray[x-1:x+2,y])+newarray[x,y]*np.sum(np.logical_not(freearray[x-1:x+2,y]))
                newarray2[x,y]=watersum/3#Kernel de difusao
                if newarray2[x,y]>=MAXVOLUME*0.9 and freearray[x,y+1]>=0:
                    newfree[x,y] = freearray[x,y+1]+1
                else:
                    newfree[x,y] = -1
    return newarray2,newfree
for i in range(LENGTH):
    print(np.sum(water[i]))
    w,f = update(water[i],free[i])
    water.append(w)
    free.append(f)
with tcod.context.new(  # New window for a console of size columns×rows.
        columns=W, rows=H, tileset=tileset,
    ) as context:
        timer = 0
        t = 0
        while True:  # Main loop, runs until SystemExit is raised.
            timer+=1
            if timer>5:
                timer=0
                t = (t+1)%LENGTH
            printarray(t)
            context.present(console)  # Show the console.