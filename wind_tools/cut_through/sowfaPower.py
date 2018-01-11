import numpy as np
from scipy.interpolate import interp1d

class sowfaPower:

    def __init__(self, inputData,density,R):
        self.fCp =  interp1d(inputData['TurbineInfo']['CpCtWindSpeed']['wind_speed'],inputData['TurbineInfo']['CpCtWindSpeed']['CP'])
        self.density = density
        self.R = R

    def setR(self,R):
        self.R = R

    def sowfaPower(self,ws):
        
        Cp = self.fCp(ws)
        A = np.pi*(self.R)**2
        rho = self.density
        power = 0.5*rho*A*Cp*ws**3
        return power