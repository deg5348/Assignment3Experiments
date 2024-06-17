# Imports:
# --------
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import copy
import gymnasium as gym


# Function 1: Train Q-learning agent
# -----------
def valid_size(state,env):
    return  0 < state[0] < env.grid_size and 0 < state[1] < env.grid_size

SEQ = []
def generate_random_int_without_repeat(low, high):
    random_num = np.random.randint(low, high)
    
    if len(SEQ) > 0 and SEQ[len(SEQ) - 1] == random_num:
        random_num = SEQ[len(SEQ) - 1]
        return random_num
    else:
        SEQ.append(random_num)
        return random_num

def generate_random_rand_without_repeat():
    prev_num = None
    while True:
        random_num = np.random.rand()
        if random_num != prev_num:
            prev_num = random_num
            return random_num

def train_q_learning(env:gym.Env,
                     no_episodes,
                     epsilon,
                     epsilon_min,
                     epsilon_decay,
                     alpha,
                     gamma,
                     q_table_save_path="q_table.npy"):

    # Initialize the Q-table:
    # -----------------------
    q_table = np.zeros((env.grid_size, env.grid_size, env.action_space.n))

    # Q-learning algorithm:
    # ---------------------
    #! Step 1: Run the algorithm for fixed number of episodes
    #! -------
    isLooped = False
    state=(0,0)
    for episode in range(no_episodes):

        state, _ = env.reset()
            
        # if(valid_size(state=state,env=env) == False ):
        #     state, _ = env.reset()
            

        state = tuple(state)
        total_reward = 0

        #! Step 2: Take actions in the environment until "Done" flag is triggered
        #! -------
        while True:
            #! Step 3: Define your Exploration vs. Exploitation
            #! -------
            env.agent_health = 100
            random_rand = generate_random_rand_without_repeat()
            if random_rand < epsilon:
                # action = env.action_space.sample()  # Explore
                action=generate_random_int_without_repeat(0,5)
            else:
                action = np.argmax(q_table[state])  # Exploit

            next_state, reward, done, _ = env.step(action)
            env.render()

            next_state = tuple(next_state)
            
            
                
            total_reward += reward

            #! Step 4: Update the Q-values using the Q-value update rule
            #! -------
            q_table[state][action] = q_table[state][action] + alpha * \
                (reward + gamma *
                 np.max(q_table[next_state]) - q_table[state][action])

            state = next_state
            

            #! Step 5: Stop the episode if the agent reaches Goal or Hell-states
            #! -------
            if done:
                break

        #! Step 6: Perform epsilon decay
        #! -------
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    #! Step 7: Close the environment window
    #! -------
    env.close()
    print("Training finished.\n")

    #! Step 8: Save the trained Q-table
    #! -------
    np.save(q_table_save_path, q_table)
    print("Q Table",q_table)
    print("Saved the Q-table.")


# Function 2: Visualize the Q-table
# -----------
def visualize_q_table(hell_state_coordinates=[(2, 1), (0, 4)],
                      goal_coordinates=(4, 4),
                      actions=["Up", "Down", "Right", "Left"],
                      q_values_path="q_table.npy"):

    # Load the Q-table:
    # -----------------
    try:
        q_table = np.load(q_values_path)

        # Create subplots for each action:
        # --------------------------------
        _, axes = plt.subplots(1, 4, figsize=(20, 5))

        for i, action in enumerate(actions):
            ax = axes[i]
            heatmap_data = q_table[:, :, i].copy()
            print('heatmap_data: ', heatmap_data)
            

            # Mask the goal state's Q-value for visualization:
            # ------------------------------------------------
            mask = np.zeros_like(heatmap_data, dtype=bool)
            mask[goal_coordinates] = True
            mask[hell_state_coordinates[0]] = True
            mask[hell_state_coordinates[1]] = True

            sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="viridis",
                        ax=ax, cbar=False, mask=mask, annot_kws={"size": 9})

            # Denote Goal and Hell states:
            # ----------------------------
            ax.text(goal_coordinates[1] + 0.5, goal_coordinates[0] + 0.5, 'G', color='green',
                    ha='center', va='center', weight='bold', fontsize=14)
            
            ax.text(hell_state_coordinates[0][1] + 0.5, hell_state_coordinates[0][0] + 0.5, 'H', color='red',
                    ha='center', va='center', weight='bold', fontsize=14)
            ax.text(hell_state_coordinates[1][1] + 0.5, hell_state_coordinates[1][0] + 0.5, 'H', color='red',
                    ha='center', va='center', weight='bold', fontsize=14)

            ax.set_title(f'Action: {action}')

        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print("No saved Q-table was found. Please train the Q-learning agent first or check your path.")
        
        
        
def test_q_table(env:gym.Env,
                     no_episodes,
                     epsilon,
                     epsilon_min,
                     epsilon_decay,
                     alpha,
                     gamma,
                     q_table_save_path="q_table.npy"):

    # Loading the Q-table
    loaded_q_table = np.load(q_table_save_path)
    
    state, _ = env.reset(train=False)
    state = tuple(state)
    total_reward = 0
    path = [state]

    while True:
        # Choose the action with the highest positive Q-value
        positive_q_indices = np.where(loaded_q_table[state] > 0)[0]
        print('positive_q_indices: ', positive_q_indices)
        if len(positive_q_indices) > 0:
            action = np.random.choice(positive_q_indices)
        else:
            action = np.argmax(loaded_q_table[state])

        print("ACTION IN TESTING: ",action)
        next_state, reward, done, _ = env.step(action)
        env.render()

        next_state = tuple(next_state)
        total_reward += reward
        path.append(next_state)

        state = next_state

        if done:
            break

    print(f"Test Path: {path}")
    print(f"Total Reward: {total_reward}")
    