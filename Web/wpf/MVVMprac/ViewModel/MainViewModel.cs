using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel;
using System.Windows.Navigation;

namespace MVVMprac.ViewModel
{
    class MainViewModel : INotifyPropertyChanged
    {

        private Model.MainModel model = null;
        public MainViewModel()
        {
            model = new Model.MainModel();
        }
        public Model.MainModel Model
        {
            get {return model;}
            set { model = value; OnPropertyChanged("Model"); }
        }

        

        public event PropertyChangedEventHandler? PropertyChanged;
        protected void OnPropertyChanged(string name)
        {
            PropertyChangedEventHandler handler = PropertyChanged;
            if (handler != null)
            {
                handler(this, new PropertyChangedEventArgs(name));
            }
        }

    }
}
