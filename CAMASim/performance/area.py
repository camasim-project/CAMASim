class AreaEval:
    def __init__(
        self,
        arch_config,
        array_config,
        array_cost,
        peripheral_cost,
        num_array,
        num_mat,
        num_bank,
        array_peripherals,
        mat_peripherals,
        bank_peripherals,
    ):
        """
        Initialize the AreaEval component.
        """
        self.arch_config = arch_config
        self.array_config = array_config
        self.array_cost = array_cost
        self.peripheral_cost = peripheral_cost
        self.num_array = num_array
        self.num_mat = num_mat
        self.num_bank = num_bank
        self.array_peripherals = array_peripherals
        self.mat_peripherals = mat_peripherals
        self.bank_peripherals = bank_peripherals

    def calculate_query_area(self):
        """
        Calculate the area consumption for a query operation.

        Returns:
            float: Total query area (in mm^2).

        This method calculates the total area required for a query operation, including array, interconnect, and peripheral area.
        """
        array_area = (
            (
                self.array_cost["interconnect"]["area"]
                + self.array_cost["subarray"]["area"]
            )
            * self.arch_config["SubarraysPerArray"]
            * max(self.arch_config["ArraysPerMat"], self.num_array)
            * max(self.arch_config["MatsPerBank"], self.num_mat)
            * self.num_bank
        )

        array_area += (
            (self.array_cost["peripheral"]["area"])
            * max(self.arch_config["ArraysPerMat"], self.num_array)
            * max(self.arch_config["MatsPerBank"], self.num_mat)
            * self.num_bank
        )

        array_peripheral_area = self.estimate_peripheral_area(
            self.array_peripherals
        )
        mat_peripheral_area = self.estimate_peripheral_area(self.mat_peripherals)
        bank_peripheral_area = self.estimate_peripheral_area(self.bank_peripherals)

        total_area = (
            array_area
            + array_peripheral_area
            + mat_peripheral_area
            + bank_peripheral_area
        )
        icnt_area = 0.1 * total_area
        total_area += icnt_area

        print("Area Breakdown:")
        print(f" - array area: {array_area} mm2")
        print(f" - peripheral area: {array_peripheral_area + mat_peripheral_area + bank_peripheral_area}mm2")
        # print(f" - interconnect area: {icnt_area}mm2 \n")
        return total_area

    def calculate_write_area(self):
        """
        Calculate the area  for a write operation.

        Returns:
            float: Total write area  (in mm^2).

        This method calculates the total area required for a write operation, including array, interconnect, and peripheral area.
        """
        array_area = (
            self.array_cost["write"]["area"]
            * self.num_array
            * self.num_mat
            * self.num_bank
            + self.array_cost["interconnect"]["area"]
            + self.array_cost["peripheral"]["area"]
        )

        array_peripheral_area = self.estimate_peripheral_area(
            self.array_peripherals
        )
        mat_peripheral_area = self.estimate_peripheral_area(self.mat_peripherals)
        bank_peripheral_area = self.estimate_peripheral_area(self.bank_peripherals)

        total_area = (
            array_area
            + array_peripheral_area
            + mat_peripheral_area
            + bank_peripheral_area
        )
        return total_area

    def estimate_peripheral_area(self, peripherals):
        """
        Estimate the total area of peripherals.

        Args:
            peripherals (dict): Dictionary of peripherals with their parameters.

        Returns:
            float: Total area of peripherals (in mm^2).

        This method estimates the total area of peripherals based on the given peripherals and their parameters.
        """
        total_area = 0
        for peripheral, params in peripherals.items():
            num = params["num"]
            size = params["size"]
            area = self.peripheral_cost[peripheral]["area"]
            total_area += num * size * area
        return total_area
