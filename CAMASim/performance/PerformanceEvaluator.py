from CAMASim.performance.cost import get_component_cost, get_EVACAM_cost
from CAMASim.performance.energy import EnergyEval
from CAMASim.performance.latency import LatencyEval
from CAMASim.performance.area import AreaEval


class PerformanceEvaluator:
    def __init__(self, arch_config, array_config, cell_config):
        """
        Initialize the PerformanceEvaluator with architecture and array configurations.
        """
        self.arch_config = arch_config
        self.array_config = array_config
        self.cell_config = cell_config

    def initialize(self, cam_arch):
        """
        Initialize the PerformanceEvaluator with estimated CAM architecture and components for latency and energy evaluation.

        Args:
            cam_arch (dict): Estimated CAM architecture parameters.

        This method initializes components for latency and energy evaluation based on the estimated CAM architecture.
        """
        self.cam_arch = cam_arch
        self.peripheral_cost, _ = get_component_cost()
        self.extract_arch_arrays()
        self.extract_arch_peripherals()
        self.latency_eval = LatencyEval(
            self.arch_config,
            self.array_config,
            self.array_cost,
            self.peripheral_cost,
            self.num_array,
            self.num_mat,
            self.num_bank,
            self.array_peripherals,
            self.mat_peripherals,
            self.bank_peripherals,
        )
        self.energy_eval = EnergyEval(
            self.arch_config,
            self.array_config,
            self.array_cost,
            self.peripheral_cost,
            self.num_array,
            self.num_mat,
            self.num_bank,
            self.array_peripherals,
            self.mat_peripherals,
            self.bank_peripherals,
        )

        self.area_eval = AreaEval(
            self.arch_config,
            self.array_config,
            self.array_cost,
            self.peripheral_cost,
            self.num_array,
            self.num_mat,
            self.num_bank,
            self.array_peripherals,
            self.mat_peripherals,
            self.bank_peripherals,
        )  

    def write(self, data):
        """
        Calculate the latency and energy consumption for a write operation.

        Args:
            data (numpy.ndarray): Input data for write operation.

        Returns:
            float: Latency (in nanoseconds) for the write operation.
            float: Energy consumption (in joules) for the write operation.

        This method calculates the latency and energy consumption for a write operation using the latency and energy evaluation components.
        """
        latency = self.latency_eval.calculate_write_latency()
        # todo: add write data size
        energy = self.energy_eval.calculate_write_energy()
        return latency, energy

    def query(self, data):
        """
        Calculate the latency and energy consumption for a query operation.

        Args:
            data (numpy.ndarray): Input data for query operation.

        Returns:
            float: Latency (in nanoseconds) for the query operation.
            float: Energy consumption (in joules) for the query operation.

        This method calculates the latency and energy consumption for a query operation using the latency and energy evaluation components.
        """

        latency = self.latency_eval.calculate_query_latency()
        energy = self.energy_eval.calculate_query_energy()
        self.area_eval.calculate_query_area()

        return latency, energy

    def extract_arch_arrays(self):
        """
        Extract the number of arrays and associated costs based on array configuration.

        This method extracts the number of arrays and associated costs based on array configuration parameters.
        """
        self.num_array = self.cam_arch["array"]["size"]
        self.num_mat = self.cam_arch["mat"]["size"]
        self.num_bank = self.cam_arch["bank"]["size"]
        print("ola", self.cam_arch)
        if self.array_config.get("useEVACAMCost", False):
            self.array_cost = get_EVACAM_cost(self.array_config, self.cell_config)
            print('Extracting circuit cost from EvaCAM \n')
        elif self.array_config["col"] <= 256:
            if self.array_config["bit"] == 1:
                self.cam_name = "TCAM" + "_" + str(self.array_config["col"])
            elif self.array_config["bit"] == 2:
                self.cam_name = "MCAM2b" + "_" + str(self.array_config["col"])
            elif self.array_config["bit"] == 3:
                self.cam_name = "MCAM3b" + "_" + str(self.array_config["col"])
            _, array_cost = get_component_cost()
            self.array_cost = array_cost[self.cam_name]
            print('Extracting circuit cost from user-defined cost_config.json file \n')
        else:
            print('No EvaCAM Specified or no user-defined cost_config.json \n')
            raise NotImplementedError

        assert self.array_cost is not None, "invalid array config!"

    def extract_arch_peripherals(self):
        """
        Extract the peripherals for arrays, mats, and banks based on architecture configuration.

        This method extracts the peripheral components (decoder, encoder, adder, register) for arrays, mats, and banks
        based on architecture configuration.
        """
        self.array_peripherals = self.cam_arch["array"]["peripherals"]
        self.mat_peripherals = self.cam_arch["mat"]["peripherals"]
        self.bank_peripherals = self.cam_arch["bank"]["peripherals"]
