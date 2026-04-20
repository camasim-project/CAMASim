import numpy as np

import CAMASim.function.module.rram_noise as rram_noise
from CAMASim.function.quantize import quantize_tensor


class writeNoise:
    def __init__(self, noise_config: dict) -> None:
        self.config = noise_config
        self.hasNoise = noise_config.get("hasWriteNoise", False)
        if not self.hasNoise:
            return
        self.noiseTypes = noise_config["noiseType"]
        self.cellDesign = noise_config["cellDesign"]
        self.minConductance = noise_config["minConductance"]
        self.maxConductance = noise_config["maxConductance"]

        allNoise2funcs = {
            "RRAM": {
                "volt2Physical": rram_noise.Vbd2conduct,
                "quantization": self.__add_RRAM_quantization,
                "variation": self.__add_RRAM_variation,
                "physical2Volt": rram_noise.conduct2Vbd,
            },
            "Numerical": {
                "volt2Physical": self.__nop,
                "variation": self.__add_numerical_variation,
                "physical2Volt": self.__nop,
            },
        }

        self.noise2func = allNoise2funcs[noise_config["device"]]

    def add_write_noise(self, data: np.ndarray) -> np.ndarray:
        assert len(data.shape) == 2 or (
            len(data.shape) == 3 and data.shape[2] == 2
        ), "ERROR: VbdArray should be a 2-D or 3-D array"

        if not self.hasNoise or not self.noiseTypes:
            return data  # do not has write noise, return directly
        data = self.noise2func["volt2Physical"](data, self.cellDesign)
        for noiseType in self.noiseTypes:
            data = self.noise2func[noiseType](data, self.config[noiseType])
        result = self.noise2func["physical2Volt"](data, self.cellDesign)

        return result

    def __add_RRAM_quantization(
        self, conductArray: np.ndarray, config: dict
    ) -> np.ndarray:
        nBits = self.config["quantization"]["nBits"]
        assert nBits > 1, "ERROR: quant bit cannot be less or equal than 1"
        quantLevel, min_val, max_val = quantize_tensor(
            conductArray,
            num_bits=nBits,
            min_val=self.minConductance,
            max_val=self.maxConductance,
        )

        quantStep = (max_val - min_val) / (2 ** (nBits) - 1)
        quantConduct = min_val + quantLevel * quantStep

        return quantConduct

    def __add_RRAM_variation(
        self, conductArray: np.ndarray, config: dict
    ) -> np.ndarray:
        if self.config["variation"]["type"] == "gaussian":
            stdDev = self.config["variation"]["stdDev"]
            noise = np.random.normal(0, stdDev, conductArray.shape)
            conductArray += noise
        elif self.config["variation"]["type"] == "g-dependent":
            conductArray = rram_noise.addConduDependentVar(conductArray)
        else:
            raise NotImplementedError(
                "Variation type not implemented. Please check config file."
            )

        return conductArray

    def __add_numerical_variation(self, array: np.ndarray, config: dict) -> np.ndarray:
        if self.config["variation"]["type"] == "gaussian":
            if (stdDev := self.config.get("variation", {}).get("stdDev")) is None:
                raise KeyError("Configuration missing 'variation.stdDev'")            
            noise = np.random.normal(0, stdDev, array.shape)
            array += noise
        elif self.config["variation"]["type"] == "bitflip":
            if (variation := self.config.get("variation", {}).get("value")) is None:
                raise KeyError("Configuration missing 'variation.value'")
            r = np.random.random(array.shape)
            # The only bits that flip are the ones.
            flip_mask = (array == 1) & (r < variation)
            array[flip_mask] = 0
        else:
            raise NotImplementedError(
                "Variation type not implemented. Please check config file."
            )

        return array

    def __nop(self, x, cellDesign):
        return x
