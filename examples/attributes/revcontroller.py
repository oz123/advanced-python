from datetime import datetime as dt
class RevController:
    "records all mutations to disk"
    def __setattr__(self, name, value):
        with open("RevController.txt", "a+") as f:
            f.write("{} {} {}\n".format(dt.utcnow(),
                                        name, value))
        super().__setattr__(name, value)
rc = RevController()
rc.a = 1
print(rc.a)
rc.a = 2
print(rc.a)
