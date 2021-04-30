import time

import numpy as np
from agentMET4FOF.agents import AgentMET4FOF
from matplotlib import pyplot as plt
from sklearn import linear_model
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from .zema_feature_extract import FFT_BFC, Pearson_FeatureSelection


class FFTAgent(AgentMET4FOF):
    def init_parameters(self, sampling_period=1):
        self.sampling_period = sampling_period                                                                   # sampling period 1 s                                      # sampling points

    def on_received_message(self, message):
        x_data = message['data']['quantities']
        n_of_sampling_pts = x_data.shape[1]
        freq = np.fft.rfftfreq(n_of_sampling_pts, float(self.sampling_period)/n_of_sampling_pts)   # frequency axis
        amp = np.fft.rfft(x_data[0,:,0])                                                      # amplitude axis
        self.send_output({"freq": freq, "x":np.abs(amp)})

class FFT_BFCAgent(AgentMET4FOF):
    def init_parameters(self, perc_feat=10):
        self.percentage_features = perc_feat
        self.fft_bfc = FFT_BFC(perc_feat=self.percentage_features)

    def on_received_message(self, message):
        if message['channel'] == 'train':
            res = self.fft_bfc.fit_transform(message['data']['quantities'])
            self.send_output({'quantities': res, 'target': message['data']['target']}, channel='train')
            self.send_plot(self.fft_bfc.plot_bestFreq())

        elif message['channel'] == 'test':
            res = self.fft_bfc.transform(message['data']['quantities'])
            self.send_output({'quantities': res, 'target': message['data']['target']}, channel='test')

class TrainTestSplitAgent(AgentMET4FOF):
    """
    This agent sets the data for train-test phases. There are two modes: Hold-out and Prequential (for incremental learning only)

    In hold-out mode, every batch of data is split into train-test with a prefixed ratio.
    In prequential mode, every batch of data is first fully tested and then trained.

    """
    def init_parameters(self, train_ratio=0.8):
        """
        train_ratio : float
            The ratio of training data in splitting the batch of data. The test_ratio then, is 1 - train_ratio.
            When train_ratio is -1, the mode is set to prequential, that is the whole batch of data is sent for testing and then training.
        """

        self.train_ratio = train_ratio

        if train_ratio > 0:
            self.pretrain_done = True
        else:
            self.pretrain_done = False

    def on_received_message(self, message):
        x_data = message['data']['quantities']
        y_data = message['data']['target']

        #leave one out
        if self.train_ratio > 0:
            x_train, x_test =train_test_split(x_data, train_size=self.train_ratio,random_state=15)
            y_train, y_test =train_test_split(y_data, train_size=self.train_ratio,random_state=15)

            #so that train and test will be handled sequentially
            self.send_output({'quantities': x_train, 'target': y_train}, channel='train')
            time.sleep(2)
            self.send_output({'quantities': x_test, 'target': y_test}, channel='test')

        #prequential
        else:
            if self.pretrain_done == False:
                self.pretrain_done= True
                self.send_output({'quantities': x_data, 'target': y_data}, channel='train')
                time.sleep(2)
            else:
                self.send_output({'quantities': x_data,'target': y_data}, channel='test')
                time.sleep(2)
                self.send_output({'quantities': x_data,'target': y_data}, channel='train')

class Pearson_FeatureSelectionAgent(AgentMET4FOF):
    def init_parameters(self):
        self.pearson_fs = Pearson_FeatureSelection()

    def on_received_message(self, message):
        if message['channel'] == 'train':
            #handle train data
            selected_features, sensor_percentages = self.pearson_fs.fit_transform(message['data']['quantities'], message['data']['target'])
            self.send_output({'quantities':np.array(selected_features),'target':message['data']['target']}, channel='train')
            self.send_plot(self.pearson_fs.plot_feature_percentages(sensor_percentages,
                                                                    labels=('Microphone',
                                                                            'Vibration plain bearing','Vibration piston rod','Vibration ball bearing',
                                                                            'Axial force','Pressure','Velocity','Active current','Motor current phase 1',
                                                                            'Motor current phase 2','Motor current phase 3')))
            #handle test data
        elif message['channel'] == 'test':
            selected_features, sensor_percentages = self.pearson_fs.transform(message['data']['quantities'])
            self.send_output({'quantities':np.array(selected_features), 'target':message['data']['target']}, channel='test')
            self.log_info("HANDLING TEST DATA NOW")

class LDA_Agent(AgentMET4FOF):
    def init_parameters(self, incremental = True):
        self.ml_model = LinearDiscriminantAnalysis(n_components=3,priors=None, shrinkage=None, solver='eigen')
        self.incremental = incremental

    def reformat_target(self, target_vector):
        class_target_vector=np.ceil(target_vector[0])
        for i in class_target_vector.index:
            if class_target_vector[i]==0:
                class_target_vector[i]=1                   #Fixing the zero element.
        return np.array(class_target_vector)

    def on_received_message(self, message):
        self.log_info("MODE : "+ message['channel'])
        if message['channel'] == 'train':
            if self.incremental:
                #message['data']['target'] = message['data']['target'][0]
                message['data']['target'] = self.reformat_target(message['data']['target'])
                self.buffer_store(agent_from=message['from'], data=message['data'])
                y_true = self.buffer[list(self.buffer.keys())[0]]['target']
                x = np.array(self.buffer[list(self.buffer.keys())[0]]['quantities'])
            else:
                y_true = self.reformat_target(message['data']['target'])
                x = message['data']['quantities']
            self.ml_model = self.ml_model.fit(x, y_true)
            self.log_info("Overall Train Score: " + str(self.ml_model.score(x, y_true)))

        elif message['channel'] == 'test':
            y_true = self.reformat_target(message['data']['target'])
            y_pred = self.ml_model.predict(message['data']['quantities'])
            self.send_output({'y_pred':y_pred, 'y_true': y_true})
            self.log_info("Overall Test Score: " + str(self.ml_model.score(message['data']['quantities'], y_true)))
            self.lda_test_score = self.ml_model.score(message['data']['quantities'], y_true)


class Regression_Agent(AgentMET4FOF):
    def init_parameters(self, regression_model="BayesianRidge", incremental=True):
        self.incremental = incremental
        self.regression_model = regression_model

        if regression_model=="BayesianRidge":
            self.lin_model = linear_model.BayesianRidge()
        elif regression_model=="RandomForest":
            self.lin_model = RandomForestRegressor(n_estimators=40)
        else:
            raise Exception("Wrongly defined regression model. Available models are: 'RandomForest' and 'BayesianRidge'")

    def on_received_message(self, message):

        if message['channel'] == 'train':
            if self.incremental:
                message['data']['target'] = message['data']['target'].ravel()
                self.buffer_store(agent_from=message['from'], data=message['data'])
                y_true = self.buffer[list(self.buffer.keys())[0]]['target']
                x = np.array(self.buffer[list(self.buffer.keys())[0]]['quantities'])
            else:
                y_true = message['data']['target'][0]
                x = message['data']['quantities']
            self.lin_model = self.lin_model.fit(x, y_true)
            self.log_info("Overall Train Score: " + str(self.lin_model.score(x, y_true)))
        elif message['channel'] == 'test':
            y_true = message['data']['target'][0]
            y_pred = self.lin_model.predict(message['data']['quantities']).clip(0, 100)
            self.send_output({'y_pred': y_pred, 'y_true': np.array(y_true)})
            self.log_info("Overall Test Score: " + str(self.lin_model.score(message['data']['quantities'], y_true)))
            self.reg_test_score = self.lin_model.score(message['data']['quantities'], y_true)


class EvaluatorAgent(AgentMET4FOF):
     def on_received_message(self, message):
        self.buffer_store(agent_from=message['from'], data=message['data'])
        from_agent = message['from']
        y_pred = self.buffer[from_agent]['y_pred']
        y_true = self.buffer[from_agent]['y_true']
        error = np.abs(y_pred- y_true)
        rmse = np.sqrt(mean_squared_error(y_pred, y_true))

        self.log_info(message['from']+": Root mean squared error of classification is:" + str(rmse))
        self.send_output({message['from']: rmse})

        #send plot
        graph_comparison = self.plot_comparison(y_true, y_pred,
                                                from_agent=message['from'],
                                                sum_performance="RMSE: " + str(rmse))
        self.send_plot({message['from']:graph_comparison})

     def plot_comparison(self, y_true, y_pred, from_agent = None, sum_performance= ""):
         if from_agent is not None: #optional
            agent_name = from_agent
         else:
            agent_name = ""
         fig, ax = plt.subplots()
         ax.scatter(y_true,y_pred)
         fig.suptitle("Prediction vs True Label: " + agent_name)
         ax.set_title(sum_performance)
         ax.set_xlabel("Y True")
         ax.set_ylabel("Y Pred")
         return fig
