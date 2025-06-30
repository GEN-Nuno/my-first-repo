class Observer:
    """Observer interface"""
    def update(self, subject):
        """Update method called when subject changes"""
        pass

class Subject:
    """Subject that notifies observers of changes"""
    
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        """Detach an observer"""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self):
        """Notify all observers of a change"""
        for observer in self._observers:
            observer.update(self)
