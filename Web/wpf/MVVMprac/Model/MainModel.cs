using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel;

namespace MVVMprac.Model
{
    // Model :  View Model에서 사용할 데이터를 정의
    class MainModel : INotifyPropertyChanged
    {

        private int num = 1;
        private int num2 = 1;


        public int Num
        {
            get
            {
                return num;
            }
            set
            {
                num = value;
                Num2 = value * 2;
                // UI에 바인딩된 변수가 변경되었을 떄 UI를 업데이트 할 수 있도록 알려주는 함수

                OnPropertyChanged("Num");
            }

        }

        public int Num2
        {
            get
            {
                return num2;
            }
            set
            {
                num2 = value;
                OnPropertyChanged("Num2");
            }
        }




        // 용도가 무엇일까
        /*
         MVVM패턴을 사용하기 위해 필수적으로 구현해야하는 인터페이스
         https://blog.naver.com/vactorman/220486213754 확인해보기
         - 데이터를 UI에 바인딩 했을 때 실시간으로 업데이트하기 위해서 사용된다.
         */
        public event PropertyChangedEventHandler? PropertyChanged;

        protected void OnPropertyChanged(string propertyName)
        {
            if (PropertyChanged != null)
            {
                PropertyChanged(this, new PropertyChangedEventArgs(propertyName));
            }
        }


    }
}
