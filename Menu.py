

class MenuItem(object):
    def __init__(self, name):
        self.name = name
        self.options = {}

    def use(self):
        print("====================")
        for k, v in self.options.items():
            print(k, v.__name__)
        print("====================")
        my_input = input("which option?")
        if my_input in self.options:
            ret_val = self.options[my_input]()
            if isinstance(ret_val, MenuItem):
                return ret_val
            else:
                return self

    def jump_here(self):
        return self

def t1():
    print("t1")


def t2():
    print("t2")


def t3():
    print("t3")


def t4():
    print("t4")


if __name__ == "__main__":
    start_item = MenuItem("m_1")
    item = MenuItem("m2")
    start_item.options["t1"] = t1
    start_item.options["submenu"] = item

    item.options["t2"] = t2
    item.options["return"] = start_item.jump_here



    current_item = start_item



    current_item = current_item.use()

