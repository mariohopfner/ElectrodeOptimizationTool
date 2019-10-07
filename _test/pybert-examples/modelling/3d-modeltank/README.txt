This is a synthetic model of an experimental tank with a high resistive heterogeneity motivated by the BAM Berlin.

Geometry: 0.99m x 0.5m x 1.0m 
Data: 48 Electrodes and 588 Measurements defined in modeltank.shm and are distributed an both sides of the tank.

We use the poly tools to create a PLC of the tank and an inhomogeneity, mesh it using tetgen and finally call the modelling routine twice once for the homogeneous and the heterogeneous case

Files:
    calc.sh -- the main calculation script for homogeneous and inhomogeneous modelling examples

    tankPLC.sh -- Utility function that create the PLC
    
    modeltank.shm -- configuration for measurement
