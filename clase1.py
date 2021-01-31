# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import flopy

#parametros iniciales
name = "modelo_enero_18"
h1 = 100
h2 = 90
Nlay = 10
N = 101
L = 400.0
H = 50.0
k = 1.0


#busco mfg en la carpeta especificada y guardo los archivos
sim = flopy.mf6.MFSimulation(
    sim_name=name, exe_name="C:/WRDAPP/mf6.2.0/bin/mf6", version="mf6", sim_ws="workspace"
)


#crea objetos de flopy TDIS
tdis = flopy.mf6.ModflowTdis(
    sim, pname="tdis", time_units="DAYS", nper=1, perioddata=[(1.0, 1, 1.0)]
)

# crea el paquete de objetos de flopy ims
ims = flopy.mf6.ModflowIms(sim, pname="ims", complexity="SIMPLE")

#crea el modelo de flujo de agua
model_nam_file = "{}.nam".format(name)
gwf = flopy.mf6.ModflowGwf(sim, modelname=name, model_nam_file=model_nam_file)


#crear el paquete de discretacion
bot = np.linspace(-H / Nlay, -H, Nlay)
delrow = delcol = L / (N - 1) #espesor de fias
dis = flopy.mf6.ModflowGwfdis( #paquete de discretizacion
    gwf,
    nlay=Nlay,
    nrow=N,
    ncol=N,
    delr=delrow,
    delc=delcol,
    top=0.0,
    botm=bot,
)

#crear el paquete de valores iniciales
start = h1 * np.ones((Nlay, N, N))
ic = flopy.mf6.ModflowGwfic(gwf, pname="ic", strt=start)


#Crear el paquete de flujo de propiedades de nodo_ controla el flujo entre celdas
npf = flopy.mf6.ModflowGwfnpf(gwf, icelltype=1, k=k, save_flows=True)

#
chd_rec = []
chd_rec.append(((0, int(N / 4), int(N / 4)), h2))
for layer in range(0, Nlay):
    for row_col in range(0, N):
        chd_rec.append(((layer, row_col, 0), h1))
        chd_rec.append(((layer, row_col, N - 1), h1))
        if row_col != 0 and row_col != N - 1:
            chd_rec.append(((layer, 0, row_col), h1))
            chd_rec.append(((layer, N - 1, row_col), h1))
chd = flopy.mf6.ModflowGwfchd(
    gwf,
    maxbound=len(chd_rec),
    stress_period_data=chd_rec,
    save_flows=True,
) 

#
iper = 0
ra = chd.stress_period_data.get_data(key=iper)
ra


# Create the output control (`OC`) Package
headfile = "{}.hds".format(name)
head_filerecord = [headfile]
budgetfile = "{}.cbb".format(name)
budget_filerecord = [budgetfile]
saverecord = [("HEAD", "ALL"), ("BUDGET", "ALL")]
printrecord = [("HEAD", "LAST")]
oc = flopy.mf6.ModflowGwfoc(
    gwf,
    saverecord=saverecord,
    head_filerecord=head_filerecord,
    budget_filerecord=budget_filerecord,
    printrecord=printrecord,
)

#construir los .txt
sim.write_simulation()

# condicion de exito
success, buff = sim.run_simulation()
if not success:
    raise Exception("MODFLOW 6 did not terminate normally.")









