from metrics.data_calculator_interface import Data_Calculator_Interface
#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
#Avoiding duplicated work
class Data_Provider_Interface(Data_Calculator_Interface):

    def __init__(self):
        pass

    #All providers are singeltons. We want single provider for each type of data
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Data_Provider_Interface, cls).__new__(cls)
            #initialize subclass data structure
            cls.instance.reset_data()
        return cls.instance
    
    #Returns the data of the data provider
    def get_data(self):
        return None