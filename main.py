import argparse
import gymnasium as gym
from stable_baselines3 import DDPG
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.vec_env import DummyVecEnv
import numpy as np

# Setting up the argument parser for command-line inputs
parser = argparse.ArgumentParser()

# Device to run the code on (CPU or GPU)
parser.add_argument('--device', type=str, default='cpu', help='Specify device: cpu or cuda')

# Whether to train the model
parser.add_argument('--train', type=bool, default=False, help='Train the model (True/False)')

# Whether to load a pre-trained model
parser.add_argument('--load', type=bool, default=True, help='Load a pre-trained model (True/False)')

# Path to save the trained model
parser.add_argument('--save_path', default=None, help='Path to save the model (set to None to skip saving)')

# Number of episodes for evaluation
parser.add_argument('--eval_episodes', type=int, default=10, help='Number of episodes for evaluation')

# Total timesteps to train the model
parser.add_argument('--train_timesteps', type=int, default=None, help='Number of timesteps for training (set to None to skip training)')

# Maximum steps allowed per episode
parser.add_argument('--max_episode_step', type=int, default=None, help='Maximum steps allowed per episode.')

# Parse the input arguments
args = parser.parse_args()

# Extract parsed arguments for convenience
device = args.device
load = args.load
train_timesteps = args.train_timesteps
eval_episodes = args.eval_episodes
max_episode_step = args.max_episode_step
save_path = args.save_path

# Register the custom CartPoleSwingUp environment with Gym
gym.register(
    id='CartPoleSwingUp',
    entry_point='myCartpoleF_SwingUp:CartPoleSwingUp',  # Custom environment location
    reward_threshold=0,  # Reward threshold for environment completion
    max_episode_steps=max_episode_step  # Maximum steps per episode
)

# Create a vectorized environment with rendering enabled
env = DummyVecEnv([lambda: gym.make('CartPoleSwingUp', render_mode='human')])

# Load or initialize the DDPG model
if load:
    print("Loading the pre-trained model...")
    model = DDPG.load('model/swing_up.zip', env=env)
else:
    # Add noise to actions for exploration during training
    action_noise = NormalActionNoise(
        mean=np.zeros(env.action_space.shape),
        sigma=0.1 * np.ones(env.action_space.shape)
    )

    # Initialize a new DDPG model with a custom neural network architecture
    model = DDPG(
        'MlpPolicy',
        env,
        policy_kwargs=dict(net_arch=[36, 48, 16]),
        action_noise=action_noise
    )

# Train the model if the user specifies a training duration
if train_timesteps:
    print('--------------Training the Model--------------')
    model.learn(total_timesteps=train_timesteps)

# Evaluate the model
print('--------------Evaluating the Model--------------')
for episode in range(eval_episodes):
    obs = env.reset()  # Reset the environment at the start of each episode
    done = False
    total_reward = 0  # Accumulate rewards for this episode
    while not done:
        action, _ = model.predict(obs, deterministic=False)  # Predict the action
        obs, reward, done, info = env.step(action)  # Take the action and observe the result
        total_reward += reward  # Add the reward to the total
        env.render()  # Render the environment
    print(f'Episode: {episode + 1} | Total Reward: {total_reward}')

# Save the trained model if a save path is specified
if save_path:
    print(f"Saving the model to {save_path}...")
    model.save(save_path)

# Close the environment
env.close()
