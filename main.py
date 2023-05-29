from PyQt5.QtWidgets import *
from PyQt5 import uic
import os
from external import *


class MainWindow(QMainWindow):

    # Размеры окна под каждую вкладку
    tab_sizes = {
        0: (892, 320),
        1: (1000, 420)
    }

    def __init__(self):
        super().__init__()
        print(os.getcwd())
        uic.loadUi('./interface.ui', self)
        self.show()

        # Настройка размеров окна
        self.setFixedWidth(self.tab_sizes[0][0])
        self.setFixedHeight(self.tab_sizes[0][1])

        self._connect_event_handlers()

        self.basePeriodFileVariables = None
        self.reportPeriodFileVariables = None

        # Открытие первой вкладки
        self.tabWidget.setCurrentIndex(0)

    # Добавляет обработчики на элементы
    def _connect_event_handlers(self):
        self.tabWidget.tabBarClicked.connect(self.window_resize)

        self.buttonOpenFileBasePeriodValues.clicked.connect(self.select_open_file)
        self.buttonOpenFileReportPeriodValues.clicked.connect(self.select_open_file)
        self.buttonOpenFileIntervalForecast.clicked.connect(self.select_open_file)
        self.buttonOpenFileActualValues.clicked.connect(self.select_open_file)

        self.buttonGetPointEstimate.clicked.connect(self.get_estimate)
        self.buttonGetIntervalEstimate.clicked.connect(self.get_estimate)
        self.buttonReset1.clicked.connect(self.reset)
        self.buttonReset2.clicked.connect(self.reset)

    # Изменяет размеры окна в соответствии с выбранной вкладкой
    def window_resize(self, index):
        size = self.tab_sizes[index]
        self.setFixedWidth(size[0])
        self.setFixedHeight(size[1])

    # Открывает файл
    def select_open_file(self):

        button_tag = self.sender().objectName()

        if button_tag == 'buttonOpenFileBasePeriodValues':
            caption = 'Открыть файл с данными базового периода'
            target_textbox = self.textboxBasePeriodValuesFilename
        elif button_tag == 'buttonOpenFileReportPeriodValues':
            caption = 'Открыть файл с данными отчетного периода'
            target_textbox = self.textboxBaseReportValuesFilename
        elif button_tag == 'buttonOpenFileIntervalForecast':
            caption = 'Открыть файл с данными потребления без учета ЭСМ'
            target_textbox = self.textboxIntervalForecastFilename
        else:
            caption = 'Открыть файл с данными потребления с учетом ЭСМ'
            target_textbox = self.textboxActualValuestFilename

        selected_file, _ = QFileDialog.getOpenFileName(self, caption=caption, filter='CSV (разделители - запятые) (*.csv)')
        if selected_file:
            target_textbox.setText(selected_file)

            # Определение списка доступных переменных
            varnames = get_variable_names(selected_file)
            if button_tag == 'buttonOpenFileBasePeriodValues':
                self.basePeriodFileVariables = varnames
            elif button_tag == 'buttonOpenFileReportPeriodValues':
                self.reportPeriodFileVariables = varnames

            if button_tag == 'buttonOpenFileIntervalForecast':
                self.listVariablesUpper.clear()
                self.listVariablesLower.clear()

                for varname in varnames:
                    self.listVariablesUpper.addItem(varname)
                    self.listVariablesLower.addItem(varname)

            elif button_tag == 'buttonOpenFileActualValues':
                self.listActualsVariable.clear()
                for varname in varnames:
                    self.listActualsVariable.addItem(varname)

            # Открытие списка доступных переменных, если оба файла открыты
            elif self.basePeriodFileVariables is not None and self.reportPeriodFileVariables is not None:
                shared_variables = list(set(self.basePeriodFileVariables).intersection(self.reportPeriodFileVariables))

                self.listVariables.clear()
                for varname in shared_variables:
                    self.listVariables.addItem(varname)

    # Определяет оценку эффективности
    def get_estimate(self):
        button_tag = self.sender().objectName()

        # Вычисление точечной оценки
        if button_tag == 'buttonGetPointEstimate':
            base_filepath = self.textboxBasePeriodValuesFilename.text()
            report_filepath = self.textboxBaseReportValuesFilename.text()

            if base_filepath != '' and report_filepath != '':
                efficiency = calculate_point_estimate(
                    filepath_base=base_filepath,
                    filepath_report=report_filepath,
                    feature_name=self.listVariables.currentText()
                )

                self.labelEfficiencyScore.setText(f'{efficiency:.3e} {self.listUnits1.currentText()}')

        # Вычисление инетрвальной оценки
        else:
            interval_forecast_filepath = self.textboxIntervalForecastFilename.text()
            actual_filepath = self.textboxActualValuestFilename.text()

            if interval_forecast_filepath != '' and actual_filepath != '':
                interval_efficiency = calculate_interval_estimate(
                    filepath_interval_forecast=interval_forecast_filepath,
                    filepath_actual=actual_filepath,

                    feature_name_upper=self.listVariablesUpper.currentText(),
                    feature_name_lower=self.listVariablesLower.currentText(),
                    feature_name_actual=self.listActualsVariable.currentText(),
                )

                self.labelIntervalEfficiencyUpperScore.setText(f'{interval_efficiency[0]:.3e} {self.listUnits2.currentText()}')
                self.labelIntervalEfficiencyLowerScore.setText(f'{interval_efficiency[1]:.3e} {self.listUnits2.currentText()}')

    # Сброс указанных данных
    def reset(self):
        current_tab = self.tabWidget.currentIndex()

        if current_tab == 0:
            self.listUnits1.setCurrentIndex(0)
            self.listVariables.clear()
            self.labelEfficiencyScore.setText('')
            self.textboxBasePeriodValuesFilename.setText('')
            self.textboxBaseReportValuesFilename.setText('')

        else:
            self.listUnits2.setCurrentIndex(0)
            self.listVariablesUpper.clear()
            self.listVariablesLower.clear()
            self.listActualsVariable.clear()
            self.labelIntervalEfficiencyUpperScore.setText('')
            self.labelIntervalEfficiencyLowerScore.setText('')
            self.textboxIntervalForecastFilename.setText('')
            self.textboxActualValuestFilename.setText('')


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec()
