from game.base import TurnBasedGame
from kaggle_environments import make
from enum import Enum

class ConnectFourGame(TurnBasedGame):

    # Flags
    class PlayerStatus(Enum):
        ACTIVE = 'ACTIVE'
        INACTIVE = 'INACTIVE'
        DONE = 'DONE'

    def __init__(self, base_params={}, playerZero='human', playerOne='human', num_games=2, npc_wait_time=2, **kwargs):
        super(ConnectFourGame, self).__init__(**kwargs)
        self.base_env_params = base_params
        self.npc_wait_time = npc_wait_time
        self.num_games = num_games
        self.max_players = 2
        self.base_env = None

        if playerZero != 'human':
            player_zero_id = playerZero + '_0'
            self._add_player(player_zero_id, idx=0, buff_size=1, is_human=False)

        if playerOne != 'human':
            player_zero_id = playerOne + '_1'
            self._add_player(player_zero_id, idx=1, buff_size=1, is_human=False)

    @property
    def active_player_idx(self):
        return self.player_statuses.index(self.PlayerStatus.ACTIVE)

    @property
    def active_player_id(self):
        return self.players[self.active_player_idx]

    @property
    def inactive_player_idx(self):
        return self.player_statuses.index(self.PlayerStatus.INACTIVE)

    @property
    def inactive_player_id(self):
        return self.players[self.inactive_player_idx]

    @property
    def board(self):
        p0_obs, p1_obs = [obs['observation'] for obs in self.state]
        if 'board' in p0_obs:
            return p0_obs['board']
        if 'board' in p1_obs:
            return p1_obs['board']
        raise ValueError("`board` not found in either player observation!")

    @property
    def player_statuses(self):
        if not self.base_env:
            raise ValueError("Game must be activated before player statuses are determined")
        return [self.PlayerStatus(pi['status']) for pi in self.base_env.state]

    @property
    def state(self):
        if not self.base_env:
            return None
        return self.base_env.state

    @state.setter
    def state(self, val):
        if not hasattr(self, 'base_env') or not self.base_env:
            return
        self.base_env.state = val

    def get_player_status(self, player_id=None, player_idx=None):
        if player_id is None and player_idx is None:
            raise ValueError("Either one of `player_id` or `player_idx` must be provided!")
        if player_id is not None and player_idx is not None:
            raise ValueError("Both player_id and player_idx were provided, please provided either!")
        if player_idx is None:
            player_idx = self.players.index(player_id)
        return self.player_statuses[player_idx]

    def get_default_action(self, player_id):
        # TODO
        return 0

    def advance_turn(self):
        super(ConnectFourGame, self).advance_turn()
        if self.curr_player != self.active_player_id:
            raise RuntimeError("Inconsistent state! Active player={} but current player={}".format(self.active_player_id, self.curr_player))

    def _curr_game_over(self):
        return any([status == self.PlayerStatus.DONE for status in self.player_statuses])

    def _is_last_game(self):
        return self.curr_game_number + 1 == self.num_games

    def _is_full(self):
        return self.num_players == self.max_players

    def _apply_action(self, player_idx, action):
        if not self.get_player_status(player_idx=player_idx) == self.PlayerStatus.ACTIVE:
            raise ValueError("Apply action called for player_idx={} but that player is not active!".format(player_idx))
        joint_action = [0] * self.num_players
        joint_action[player_idx] = action
        self.base_env.step(joint_action)

    def _activate(self):
        self.base_env = make('connectx', self.base_env_params)
        self.base_env.reset()

        # Here we call the super class _activate at the end as it relies on `self.state` being set
        super()._activate()

    def _to_json(self):
        obj_dict = {}
        obj_dict['state'] = self._get_state()
        return obj_dict

    def _get_state(self):
        state_dict = {}
        state_dict['board'] = self.board
        return state_dict

    def _get_policy(self, npc_id, idx):
        # TODO
        return None
