import numpy as np
import torch.multiprocessing as mp

from agentMET4FOF.agentMET4FOF.agents import AgentNetwork, DataStreamAgent, MonitorAgent
from agentMET4FOF.examples.ZEMA_EMC.zema_agents import TrainTestSplitAgent
from agentMET4FOF_bayesian_neural_network_ZeMA.bnn_agents import (
    BNN_Agent,
    BNN_Model,
    EvaluatorAgent,
    StatsFeaturesAgent,
)
from agentMET4FOF_bayesian_neural_network_ZeMA.zema_hyd_datastream import (
    ZEMA_Hyd_DataStream,
)

np.random.seed(100)

USE_CUDA = False

# output_sizes = [3,4,3,4,2]
output_sizes = [3]

# architecture = ["d1","d2","d4","d8"]
# architecture = ["d2","d4"]
# architecture = ["d2"]

# varying deepness with equal wideness
# architecture = ["d1","d1","d1","d1"]
# architecture = ["d1","d1","d1"]
# architecture = ["d1","d1"]
architecture = ["d1"]


def main():
    # if use cuda
    if USE_CUDA:
        mp.set_start_method("spawn", force=True)

    # start agent network server
    agentNetwork = AgentNetwork()

    # init agents by adding into the agent network
    datastream_agent = agentNetwork.add_agent(agentType=DataStreamAgent)

    train_test_split_agent = agentNetwork.add_agent(agentType=TrainTestSplitAgent)
    stats_features_agent = agentNetwork.add_agent(agentType=StatsFeaturesAgent)

    bnn_agents = [
        agentNetwork.add_agent(agentType=BNN_Agent) for target in output_sizes
    ]

    # evaluator_agent = agentNetwork.add_agent(agentType=EvaluatorAgent)
    evaluator_agents = [
        agentNetwork.add_agent(agentType=EvaluatorAgent) for target in output_sizes
    ]

    monitor_agent_1 = agentNetwork.add_agent(agentType=MonitorAgent)
    monitor_agent_2 = agentNetwork.add_agent(agentType=MonitorAgent)

    # init parameters
    datastream_agent.init_parameters(
        stream=ZEMA_Hyd_DataStream(), pretrain_size=-1, randomize=True
    )
    # train_test_split_agent.init_parameters(kfold=5)
    train_test_split_agent.init_parameters(train_ratio=0.8)

    for index, val in enumerate(output_sizes):
        bnn_agents[index].init_parameters(
            model=BNN_Model,
            output_size=val,
            selectY_col=index,
            architecture=architecture,
        )
    # bnn_agent.init_parameters(model=BNN_Model, output_size=4, selectY_col = 3)

    # connect agents by either way:
    agentNetwork.bind_agents(datastream_agent, train_test_split_agent)
    agentNetwork.bind_agents(train_test_split_agent, stats_features_agent)
    # agentNetwork.bind_agents(train_test_split_agent,bnn_agent)

    for index, bnn_agent in enumerate(bnn_agents):
        agentNetwork.bind_agents(stats_features_agent, bnn_agent)
        agentNetwork.bind_agents(bnn_agent, monitor_agent_1)
        agentNetwork.bind_agents(bnn_agent, evaluator_agents[index])
        agentNetwork.bind_agents(evaluator_agents[index], monitor_agent_2)

    # # set all agents states to "Running"
    agentNetwork.set_running_state()


if __name__ == "__main__":
    main()
