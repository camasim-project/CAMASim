from CAMASim.function.convert import convertToPhys
from CAMASim.function.mapping import mapping
from CAMASim.function.quantize import quantize
from CAMASim.function.search import CAMSearch
from CAMASim.function.writeNoise import writeNoise


class FuncSimulator:
    def __init__(self, array_config, query_config, cell_config, noise_config):
        """
        Initializes the FunctionSimulator class with configuration settings.

        Args:
            array_config (dict): Configuration settings for the CAM array.
            query_config (dict): Configuration settings for query.
            cell_config (dict): Configuration settings for individual CAM cells.

        Initializes various components for function simulation, including quantization, conversion, mapping, and searching.
        """
        self.array_config = array_config
        self.query_config = query_config
        self.cell_config = cell_config
        self.noise_config = noise_config

        self.quantizer = quantize(query_config)
        self.converter = convertToPhys(cell_config)
        self.mapping = mapping(cam_size=None, map_rule=None, array_config=array_config)
        self.search = CAMSearch(query_config, array_config)
        self.writeNoise = writeNoise(noise_config)

    def write(self, data):
        """
        Simulates a write operation on the CAM array.

        Args:
            data (array): Input data to be written into the CAM array.

        Performs quantization, conversion, (write noise) and data mapping for a write operation.
        """
        print(data)
        # 1. Quantization (optional for ACAM)
        if self.array_config['cell'] != 'ACAM':
            data = self.quantizer.write(data)
        print(data)
        # 2. Conversion to voltage/conductance representation
        data = self.converter.write(data)

        print(data)
        # 3. add write noise
        data = self.writeNoise.add_write_noise(data)
        print(data)

        # 4. Data mapping to CAM arrays
        self.mapping.write(data)
        print(self.mapping.CamData)

    def query(self, input):
        """
        Simulates a query operation on the CAM array.

        Args:
            input (array): Query data for the CAM array.

        Performs quantization, conversion, data mapping, and search for a query operation and returns the results.
        """
        # 1. Quantization (optional for ACAM)
        if self.array_config['cell'] != 'ACAM':
            input = self.quantizer.query(input)

        # 2. Conversion to the same representation
        input = self.converter.query(input)

        # 3. Data mapping to CAM arrays for queries
        self.mapping.query(input)

        # 4. Searching in each array and merging results
        self.search.define_search_area(self.mapping.rowCams, self.mapping.colCams)
        results = self.search.search(self.mapping.CamData, self.mapping.QueryData)

        return results
