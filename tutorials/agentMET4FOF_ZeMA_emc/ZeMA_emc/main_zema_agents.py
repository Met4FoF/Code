import numpy as np
from agentMET4FOF.agents import AgentNetwork, DataStreamAgent, MonitorAgent

from ZeMA_emc import zema_agents, zema_datastream
from ZeMA_emc.zema_agents import (EvaluatorAgent, FFT_BFCAgent, LDA_Agent,
                          Pearson_FeatureSelectionAgent, Regression_Agent,
                          TrainTestSplitAgent)
from ZeMA_emc.zema_datastream import ZEMA_DataStream

np.random.seed(100)

import matplotlib
matplotlib.use('Agg') # https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread

def main():
    # start agent network server
    agentNetwork = AgentNetwork(
        dashboard_modules=[zema_datastream,
                           zema_agents], log_filename=False, backend="mesa")
    # init agents by adding into the agent network
    datastream_agent = agentNetwork.add_agent(agentType=DataStreamAgent)
    train_test_split_agent = agentNetwork.add_agent(
        agentType=TrainTestSplitAgent)
    fft_bfc_agent = agentNetwork.add_agent(agentType=FFT_BFCAgent)
    pearson_fs_agent = agentNetwork.add_agent(
        agentType=Pearson_FeatureSelectionAgent)
    lda_agent = agentNetwork.add_agent(agentType=LDA_Agent)
    bayesianRidge_agent = agentNetwork.add_agent(agentType=Regression_Agent,
                                                 name="BayesianRidge_Agent")
    randomForest_agent = agentNetwork.add_agent(agentType=Regression_Agent,
                                                name="RandomForest_Agent")
    evaluator_agent = agentNetwork.add_agent(agentType=EvaluatorAgent)
    monitor_agent = agentNetwork.add_agent(agentType=MonitorAgent)
    # init parameters
    # incremental training
    datastream_agent.init_parameters(stream=ZEMA_DataStream(),
                                     pretrain_size=1000, batch_size=250,
                                     loop_wait=10, randomize=True)
    # batch training
    # datastream_agent.init_parameters(stream=ZEMA_DataStream(),
    # pretrain_size=-1, randomize=True)
    # hold-out or prequential mode
    # train_test_split_agent.init_parameters(train_ratio=0.8) #hold-out
    train_test_split_agent.init_parameters(train_ratio=-1)  # prequential
    # init parameters for base models
    lda_agent.init_parameters()
    bayesianRidge_agent.init_parameters(regression_model="BayesianRidge")
    randomForest_agent.init_parameters(regression_model="RandomForest")
    # bind agents
    agentNetwork.bind_agents(datastream_agent, train_test_split_agent)
    agentNetwork.bind_agents(train_test_split_agent, fft_bfc_agent)
    agentNetwork.bind_agents(fft_bfc_agent, pearson_fs_agent)
    agentNetwork.bind_agents(pearson_fs_agent, lda_agent)
    agentNetwork.bind_agents(lda_agent, evaluator_agent)
    agentNetwork.bind_agents(pearson_fs_agent, bayesianRidge_agent)
    agentNetwork.bind_agents(bayesianRidge_agent, evaluator_agent)
    agentNetwork.bind_agents(pearson_fs_agent, randomForest_agent)
    agentNetwork.bind_agents(randomForest_agent, evaluator_agent)
    # bind to monitor agents
    agentNetwork.bind_agents(fft_bfc_agent, monitor_agent)
    agentNetwork.bind_agents(pearson_fs_agent, monitor_agent)
    agentNetwork.bind_agents(evaluator_agent, monitor_agent)
    # set running state
    agentNetwork.set_running_state()

    # allow for shutting down the network after execution
    return agentNetwork


if __name__ == '__main__':
    main()
