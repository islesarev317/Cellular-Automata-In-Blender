class CellRule:
    """
    Class for calculate cellular automata rules and apply them
    """

    @classmethod
    def get_code(cls, birth_cond, survive_cond=None, ndim=3):

        # ndim = 2 --> 2-dimensional space
        # birth_cond = [3] --> a dead cell turn to life if only has 3 neighbors
        # survive_cond = [2, 3] --> a living cell stays alife if only has 2 or 3 neighbors

        if survive_cond is None:
            survive_cond = birth_cond.copy()

        area_size = 3 ** ndim  # 9 for 2d

        # 1) create rules for dead cell and for living cell

        rule_for_0 = [0 for _ in range(area_size)]
        rule_for_1 = [0 for _ in range(area_size)]
        for neighbors_cnt in birth_cond:
            rule_for_0[neighbors_cnt] = 1  # --> [0, 0, 0, 1, 0, 0, 0, 0, 0]
        for neighbors_cnt in survive_cond:
            rule_for_1[neighbors_cnt] = 1  # --> [0, 0, 1, 1, 0, 0, 0, 0, 0]

        # 2) union two parts of rules

        sum_rule_list = []
        for i in range(area_size):
            sum_rule_list.append(rule_for_0[i])
            sum_rule_list.append(rule_for_1[i])
        # --> [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # 3) convert to integer and return

        sum_rule_str = "".join([str(num) for num in sum_rule_list]).lstrip("0")  # --> 1110000000000
        code = int(sum_rule_str, 2)  # --> 7168
        return code

    @classmethod
    def get_condition(cls, code, ndim=3):

        # code = 7168

        area_size = 3 ** ndim

        # 1) convert to binary

        sum_rule_str = f"{int(code):0b}"  # --> 1110000000000
        sum_rule_list = [int(num) for num in sum_rule_str.rjust(area_size * 2, "0")]
        # --> [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # 2) split into 2 part

        rule_for_0 = sum_rule_list[0::2]  # --> [0, 0, 0, 1, 0, 0, 0, 0, 0]
        rule_for_1 = sum_rule_list[1::2]  # --> [0, 0, 1, 1, 0, 0, 0, 0, 0]

        # 3) compute birth and survive conditions and return

        birth_cond = [i for i in range(area_size) if rule_for_0[i] == 1]  # --> [3]
        survive_cond = [i for i in range(area_size) if rule_for_1[i] == 1]  # --> [2, 3]
        return birth_cond, survive_cond

    @classmethod
    def apply_rule_binary(cls, code, value, neighbors, ndim=3):
        birth_cond, survive_cond = cls.get_condition(code, ndim=ndim)
        if value == 0:
            return int(neighbors in birth_cond)
        else:
            return int(neighbors in survive_cond)

    @classmethod
    def apply_rule_lifetime(cls, code, value, neighbors, ndim=3):
        birth_cond, survive_cond = cls.get_condition(code, ndim=ndim)
        if value == 0:
            b = int(neighbors in birth_cond)
            return b * value + b
        else:
            b = int(neighbors in survive_cond)
            return b * value + b

    @classmethod
    def get_max_code(cls, ndim=3):
        return 2 ** (3 ** ndim * 2) - 1

    @classmethod
    def get_flash_point(cls, ndim=3):
        """
        all codes greater than or equal to the flash point result in uncontrolled growth
        (birth cell while no neighbors)
        """
        return 2 ** (3 ** ndim * 2 - 1)

    @classmethod
    def get_percent(cls, code, ndim=3):
        return round(code / cls.get_flash_point(ndim) * 100, 2)
