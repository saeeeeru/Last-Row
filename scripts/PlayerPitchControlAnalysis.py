import warnings

import numpy as np
import matplotlib.pyplot as plt

import Metrica_PitchControl as mpc
import Metrica_Viz as mviz


class PlayerPitchControlAnalysisPlayer(object):
    def __init__(
        self,
        df_dict,
        params,
        events,
        event_id,
        team_player_to_analyze,
        player_to_analyze,
        field_dimens=(106.0, 68.0),
        n_grid_cells_x=50,
    ):
        """
        This class is used to consolidate many of the functions that would be used to analyze the impact of an
            individual on the pitch control surface during a given event of a match
        Leveraging @EightyFivePoint's pitch control model presented in the Friends of Tracking Series, we build out a
            series of tools to help isolate individual player's impacts to pitch control.
        Using an event from the match's event DataFrame, and a specific team/player ID, this class allows us to:
            1. Calculate the amount of space occupied on the pitch (per EightyFivePoint's pitch control model) for any
                frame of a match.
            2. Calculate the difference in total space occupied by the player's team and plot the difference in pitch
                control surfaces with his/her current movement relative to a theoretical velocity vector
                (which defaults to no movement).
            3. Calculate the difference in total space occupied by the player's team and plot the difference in pitch
                control surfaces relative to if the player were not on the pitch at all.
            4.  Calculate the difference in total space occupied by the player's team and plot the difference in pitch
                control surfaces relative to if the player were in a different location on the pitch and containing a
                new velocity vector

        In the relevant functions for plotting pitch control difference and space creation, the ``replace_function``
        argument determines what type of analysis we wish to carry out.
            If replace_function=``movement``, we study the player's impact on pitch control relative to the pitch
            control if the player had a different velocity vector.
            velocity vector.
            If replace_function=``presence``, we study the player's total impact on pitch control by comparing the
            pitch control surface to the pitch control surface if the player were not on the pitch at all.
            If replace_function=``location``, we study the player's impact on pitch control relative to the pitch
            control if the player were in a different location on the pitch.

        Examples of using this class for each type of analysis are contained in the file ``player_analysis_example.py``.

        Modifications to @EightyFivePoint's code for plotting pitch control to support our new plots can be found in
        ``Metrica_viz.py``

        Initialization parameters:
        :param dict df_dict : keys=team_list, values=pd.DataFrame witb velocity for each player
        :param dict params: Dictionary of model parameters (default model parameters can be generated using
                default_model_params())
        :param pd.DataFrame events: DataFrame containing the event data
        :param int event_id: Index (not row) of the event that describes the instant at which the pitch control surface
                should be calculated
        :param str team_player_to_analyze: The team of the player whose movement we want to analyze. Must be either
                "Home" or "Away"
        :param int or str(int) player_to_analyze: The player ID of the player whose movement we want to analyze. The ID
                must be a player currently on the pitch for ``team_player_to_analyze``
        :param tuple field_dimens: tuple containing the length and width of the pitch in meters. Default is (106,68)
        :param int n_grid_cells_x: Number of pixels in the grid (in the x-direction) that covers the surface.
                Default is 50. n_grid_cells_y will be calculated based on n_grid_cells_x and the field dimensions


        """
        self.df_dict = df_dict
        self.params = params
        self.events = events
        self.event_id = event_id
        self.team_player_to_analyze = team_player_to_analyze
        self.player_to_analyze = player_to_analyze
        self.field_dimens = field_dimens
        self.n_grid_cells_x = n_grid_cells_x
        (
            self.event_pitch_control,
            self.xgrid,
            self.ygrid,
        ) = mpc.generate_pitch_control_for_event(
            event_id=self.event_id,
            events=self.events,
            df_dict=self.df_dict,
            params=self.params,
        )

    def calculate_total_space_on_pitch_team(self, pitch_control_result):
        """
        Function Description:
        This function calculates the number of square meters on the pitch occupied by the team with the ball in the
        given event. This assumes that all portions of the pitch are equal in value.

        Input Parameters:
        :param numpy.ndarray pitch_control_result: The estimates from the result of a fitted pitch control model

        Returns:
        :return: The number of meters occupied by the attacking team in a freeze frame of the data. Measured in m^2
        """

        total_space_attacking = (
            self.field_dimens[0]
            * self.field_dimens[1]
            * (pitch_control_result.sum())
            / (len(self.xgrid) * len(self.ygrid))
        )
        return total_space_attacking

    def calculate_pitch_control_replaced_velocity(
        self, replace_x_velocity=0, replace_y_velocity=0,
    ):
        """
        Function Description:
        This function calculates a pitch control surface after replacing a player's velocity vector with a new one.
        Ideally, this would be used to determine what space a player is gaining (and conceding) with his/her off the
        ball movement

        Input Parameters:
        :param float replace_x_velocity: The x vector of the velocity we would like to replace our given player with.
                Positive values will move the player toward's the home team's goal, while negative values will move the
                player towards the away team's goal. Measured in meters per second. Defaults to 0
        :param float replace_y_velocity: The y vector of the velocity we would like to replace our given player with.
                Positive values will move the player to the left side of the pitch, from the perspective of the away
                team, while negative values will move the player towards the right side of the pitch from the
                perspective of the away team. Measured in meters per second. Defaults to 0.

        Returns:
        edited_pitch_control: Pitch control surface (dimen (n_grid_cells_x,n_grid_cells_y) ) containing pitch control
                probability for the attacking team with one player's velocity changed (defaulted to not moving).
                Surface for the defending team is simply 1-PPCFa.
        xgrid: Positions of the pixels in the x-direction (field length)
        ygrid: Positions of the pixels in the y-direction (field width)
        """
        self._validate_inputs()

        # Determine which row in the tracking dataframe to use
        event_frame = self.events.loc[self.event_id]["Start Frame"]

        # Replace player's velocity datapoints with new velocity vector
        tmp_df_dict = self.df_dict.copy()
        for team, df in tmp_df_dict.items():
            if team == self.team_player_to_analyze:
                df_tmp = df.copy()
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_vx",
                ] = replace_x_velocity
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_vy",
                ] = replace_y_velocity
                tmp_df_dict[team] = df_tmp

        edited_pitch_control, xgrid, ygrid = mpc.generate_pitch_control_for_event(
            event_id=self.event_id,
            events=self.events,
            df_dict=tmp_df_dict,
            params=self.params,
            field_dimen=self.field_dimens,
            n_grid_cells_x=self.n_grid_cells_x,
        )
        return edited_pitch_control, xgrid, ygrid

    def calculate_pitch_control_without_player(self):
        """
        Function description:
        This function calculates a pitch control surface after removing the player from the pitch.
        This can be used to attribute which spaces on the pitch are controlled by the specific player, rather than the
        space occupied by his/her team.

        Returns:
        edited_pitch_control: Pitch control surface (dimen (n_grid_cells_x,n_grid_cells_y) ) containing pitch control
                probability for the attacking team after removing the relevant player from the pitch. Surface for the
                defending team is simply 1-PPCFa.
        xgrid: Positions of the pixels in the x-direction (field length)
        ygrid: Positions of the pixels in the y-direction (field width)
        """
        self._validate_inputs()
        event_frame = self.events.loc[self.event_id]["Start Frame"]

        # Replace player's datapoint nan's, so pitch control does not take into account
        # the player when computing its surface
        tmp_df_dict = self.df_dict.copy()
        for team, df in tmp_df_dict.items():
            if team == self.team_player_to_analyze:
                df_tmp = df.copy()
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_x",
                ] = np.nan
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_y",
                ] = np.nan
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_vx",
                ] = np.nan
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_vy",
                ] = np.nan
                tmp_df_dict[team] = df_tmp

        edited_pitch_control, xgrid, ygrid = mpc.generate_pitch_control_for_event(
            event_id=self.event_id,
            events=self.events,
            df_dict=tmp_df_dict,
            params=self.params,
            field_dimen=self.field_dimens,
            n_grid_cells_x=self.n_grid_cells_x,
        )
        return edited_pitch_control, xgrid, ygrid

    def calculate_pitch_control_new_location(
        self,
        relative_x_change,
        relative_y_change,
        replace_velocity=False,
        replace_x_velocity=0,
        replace_y_velocity=0,
    ):

        """
        Function description:
        This function calculates a pitch control surface after moving the player to a new location on the pitch,
        and specifying a new velocity vector for the player.
        Ideally, this function would be used to identify/illustrate where players could be located/moving towards in
        order to maximize their team's pitch control

        Input parameters:
        :param float relative_x_change: The amount to change the x coordinate of the player by before calculating the
                new pitch control model. Measured in meters
        :param float relative_y_change: The amount to change the y coordinate of the player by before calculating the
                new pitch control model. Measured in meters.
        :param bool replace_velocity: Tells us whether to replace the player's velocity vector with a new one. If False,
            the player's velocity vector will remain the same. If True, the player's velocity will be placed with the
            values in the ``replace_x_velocity`` and  replace_y_velocity`` argument. Default is False.
        :param float replace_x_velocity: The x vector of the velocity we would like to replace our given player with.
                Positive values will move the player toward's the home team's goal, while negative values will move the
                player towards the Away Team's goal. Measured in m/s. Defaults to 0.
        :param float replace_y_velocity: The y vector of the velocity we would like to replace our given player with.
                Positive values will move the player to the left side of the pitch, from the perspective of the away
                team, while negative values will move the player towards the right side of the pitch from the
                perspective of the away team. Measured in m/s. Defaults to 0.

        Returns:
        edited_pitch_control: Pitch control surface (dimen (n_grid_cells_x,n_grid_cells_y) ) containing pitch control
                probability for the attcking team with one player's velocity changed
               Surface for the defending team is just 1-PPCFa.
        xgrid: Positions of the pixels in the x-direction (field length)
        ygrid: Positions of the pixels in the y-direction (field width)
        """
        self._validate_inputs()

        if replace_velocity & (replace_x_velocity == 0) & (replace_y_velocity == 0):
            warnings.warn(
                "You have not specified a new velocity vector for the player. All analysis will assume "
                "that the player is stationary in his/her new location"
            )

        event_frame = self.events.loc[self.event_id]["Start Frame"]

        # Replace datapoints with a new location and velocity vector
        tmp_df_dict = self.df_dict.copy()
        for team, df in tmp_df_dict.items():
            if team == self.team_player_to_analyze:
                df_tmp = df.copy()
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_x",
                ] = relative_x_change
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_y",
                ] = relative_y_change
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_vx",
                ] = replace_x_velocity
                df_tmp.at[
                    event_frame,
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_vy",
                ] = replace_y_velocity
                tmp_df_dict[team] = df_tmp

        edited_pitch_control, xgrid, ygrid = mpc.generate_pitch_control_for_event(
            event_id=self.event_id,
            events=self.events,
            df_dict=tmp_df_dict,
            params=self.params,
            field_dimen=self.field_dimens,
            n_grid_cells_x=self.n_grid_cells_x,
        )
        return edited_pitch_control, xgrid, ygrid

    def calculate_pitch_control_difference(
        self,
        replace_velocity=False,
        replace_x_velocity=0,
        replace_y_velocity=0,
        relative_x_change=0,
        relative_y_change=0,
        replace_function="movement",
    ):
        """
        Function description:
        This function computes the difference in pitch control surfaces between the actual event,and the event when
        one player's attributes (velocity, position, or presence) is altered. In this function, it is strongly
        recommended to use use the arguments that are relevant to the parent pitch control calculate function, depending
        on which effect we want to study.

        Input parameters:
        :param bool replace_velocity: This determines if we should replace our velocity vector with a new vector.
            Only used if ``replace_function = 'location'``.
        :param float replace_x_velocity: The x vector of the velocity we would like to replace our given player with.
            Positive values will move the player toward's the home team's goal, while negative values will move the
            player towards the Away Team's goal. Measured in m/s. Not used if
            'replace_function' = 'presence'. Defaults to 0.
        :param float replace_y_velocity: The y vector of the velocity we would like to replace our given player with.
            Positive values will move the player to the left side of the pitch, from the perspective of the away team,
            while negative values will move the player towards the right side of the pitch from the perspective of the
            away team. Measured in m/s. Not used if ``replace_function = 'presence'`` Defaults to 0.
        :param float relative_x_change: Determines how much to move the player in the x direction,
            relative to his/her current location on the pitch. Positive values will move the player toward's the home
            team's goal, while negative values will move the player towards the Away Team's goal. Measured in meters.
            Not used if ``replace_function = 'presence'`` or ``replace_function == 'movement'``.
        :param float relative_y_change: Determines how much to move the player in the y direction,
            relative to his/her current location on the pitch. Positive values will move the player to the left side of
            the pitch, from the perspective of the away team, while negative values will move the player towards the
            right side of the pitch from the perspective of the away team. Measured in meters.
            Only used if ``replace_function='location'``.
        :param string replace_function: The type of function we are using to analyze the player.
            Must be either "movement", "presence" or "location". Defaults to "movement".
            The argument "movement" uses the function ``calculate_pitch_control_replaced_velocity`` to calculate a new
            pitch control surface, using your input for the player's new velocity. If no arguments are passed for
            velocity, it will calculate the difference in pitch control between the player's current velocity, and the
            pitch control if the player is stationary.
            The argument "presence" uses the function ``calculate_pitch_control_without_player`` to calculate a new
            pitch control surface, assuming the player is not on the pitch. The function then returns a difference in
            pitch control between the actual event, and the event if the player were not present.
            The argument "location" uses  the function ``calculate_pitch_control_new_location`` to calculate a new
            pitch control surface assuming the player is in a new location on the pitch with a new velocity vector.
            The function then returns a difference in pitch control between the actual event, and the event if the
            player were in his new location.

        Returns:
            pitch_control_difference: Difference in pitch control surfaces (dimen (n_grid_cells_x,n_grid_cells_y) )
            between the actual event, and the event with the player's movement, location and/or presence altered.
            Returns difference in pitch control with respect to the team that currently has possession of the ball
            The difference surface for the defending team is simply 1-PPCFa.
            xgrid: Positions of the pixels in the x-direction (field length)
            ygrid: Positions of the pixels in the y-direction (field width)
        """
        if replace_function == "movement":
            (
                edited_pitch_control,
                xgrid,
                ygrid,
            ) = self.calculate_pitch_control_replaced_velocity(
                replace_x_velocity=replace_x_velocity,
                replace_y_velocity=replace_y_velocity,
            )
        elif replace_function == "presence":
            (
                edited_pitch_control,
                xgrid,
                ygrid,
            ) = self.calculate_pitch_control_without_player()
        elif replace_function == "location":
            (
                edited_pitch_control,
                xgrid,
                ygrid,
            ) = self.calculate_pitch_control_new_location(
                replace_velocity=replace_velocity,
                replace_x_velocity=replace_x_velocity,
                replace_y_velocity=replace_y_velocity,
                relative_x_change=relative_x_change,
                relative_y_change=relative_y_change,
            )

        else:
            raise ValueError(
                "replace_function must be either 'movement', 'presence' or 'location'"
            )
        pitch_control_difference = self.event_pitch_control - edited_pitch_control
        return pitch_control_difference, xgrid, ygrid

    def calculate_space_created(
        self,
        replace_x_velocity=0,
        replace_y_velocity=0,
        relative_x_change=0,
        relative_y_change=0,
        replace_velocity=False,
        replace_function="movement",
    ):
        """
        Function description:
        This function calculates the total amount of space generated by a player, relative to the amount generated if
            the player's velocity, location or presence is changed. In this function, it is strongly recommended to use
            the arguments that are relevant to the parent pitch control calculation function, depending on which effect
            we want to study.

        Input parameters:
        :param float replace_x_velocity: The x vector of the velocity we would like to replace our given player with.
            Positive values will move the player toward's the home team's goal, while negative values will move the
            player towards the Away Team's goal. Measured in m/s.
            ``Not used if replace_function='presence'``
        :param float replace_y_velocity: The y vector of the velocity we would like to replace our given player with.
            Positive values will move the player to the left side of the pitch, from the perspective of the away team,
            while negative values will move the player towards the right side of the pitch from the perspective of the
            away team. Measured in m/s. Not used if ``replace_function='presence``.
        :param float relative_x_change: Determines how much to move the player in the x direction,
            relative to his/her current location on the pitch. Positive values will move the player toward's the home
            team's goal, while negative values will move the player towards the Away Team's goal. Measured in meters.
            Not used if ``replace_function = 'presence'`` or ``replace_function == 'movement'``.
        :param float relative_y_change: Determines how much to move the player in the y direction,
            relative to his/her current location on the pitch. Positive values will move the player to the left side of
            the pitch, from the perspective of the away team, while negative values will move the player towards the
            right side of the pitch from the perspective of the away team. Measured in meters.
            Only used if ``replace_function='location'``.
        :param bool replace_velocity: This determines if we should replace our velocity vector with a new vector.
            Only used if ``replace_function = 'location'``.
        :param string replace_function: The type of function we are using to analyze the player.
            Must be either "movement", "presence" or "location". Defaults to "movement". For detailed description of
            this argument, please refer to the docstring in ``calculate_pitch_control_difference``

        Returns:
         A float representing amount of pitch gained (or lost) by the player's team, relative to the amount of space
            the player's team occupied before editing the player's velocity, location or movement.
            Positive values represent space lost by the player's team after editing the player's attributes,
             while negative values represent space gained after editing the player's attributes. Measured in m^2.
        """
        team_with_possession = self.events.loc[self.event_id].Team

        (pitch_control_difference, _, _,) = self.calculate_pitch_control_difference(
            replace_x_velocity=replace_x_velocity,
            replace_y_velocity=replace_y_velocity,
            relative_x_change=relative_x_change,
            relative_y_change=relative_y_change,
            replace_function=replace_function,
            replace_velocity=replace_velocity,
        )

        pitch_control_change = self.calculate_total_space_on_pitch_team(
            pitch_control_difference
        )
        if team_with_possession == self.team_player_to_analyze:
            return pitch_control_change
        else:
            return -1 * pitch_control_change

    def plot_pitch_control_difference(
        self,
        replace_x_velocity=0,
        replace_y_velocity=0,
        relative_x_change=0,
        relative_y_change=0,
        replace_velocity=False,
        replace_function="movement",
        alpha=0.7,
        alpha_pitch_control=0.5,
        team_color_dict={"Home": "r", "Away": "b"},
    ):
        """
        Function description:
        This function plots the difference between the actual event in the match, and the event if the player's velocity,
        presence, or movement is altered. In this function, it is strongly recommended to use the arguments that are
        relevant to the parent pitch control calculation function, depending on which effect we want to study.

        If we are removing the player from the pitch (by setting ``replace_function='presence'``), this function plots
        the space that the player was occupying for his team during the given event.
        If we are altering the player's velocity vector (by setting ``replace_function='movement'``), this function
        plots the space gained by the player's current movement in the color of the player's team, and plots the space
        lost by the player's current movement in the color of the opposite team.
        If we are moving the player's location on the pitch (by setting ``replace_function='location'``), we are
        plotting the space the player's team would gain by being in the new location in the player's team color, and
        the space that the player would concede by moving to the new location in the color of the opposition team. We
        also plot the player's proposed new location and velocity in green.

        Input Parameters:
        :param float replace_x_velocity: The x vector of the velocity we would like to replace our given player with.
            Positive values will move the player toward's the home team's goal, while negative values will move the
            player towards the Away Team's goal. Measured in m/s.
            ``Not used if replace_function='presence'``
        :param float replace_y_velocity: The y vector of the velocity we would like to replace our given player with.
            Positive values will move the player to the left side of the pitch, from the perspective of the away team,
            while negative values will move the player towards the right side of the pitch from the perspective of the
            away team. Measured in m/s. Not used if ``replace_function='presence``.
        :param float relative_x_change: Determines how much to move the player in the x direction,
            relative to his/her current location on the pitch. Positive values will move the player toward's the home
            team's goal, while negative values will move the player towards the Away Team's goal. Measured in meters.
            Not used if ``replace_function = 'presence'`` or ``replace_function == 'movement'``.
        :param float relative_y_change: Determines how much to move the player in the y direction,
            relative to his/her current location on the pitch. Positive values will move the player to the left side of
            the pitch, from the perspective of the away team, while negative values will move the player towards the
            right side of the pitch from the perspective of the away team. Measured in meters.
            Only used if ``replace_function='location'``.
        :param bool replace_velocity: This determines if we should replace our velocity vector with a new vector.
            Only used if ``replace_function = 'location'``.
        :param string replace_function: The type of function we are using to analyze the player.
            Must be either "movement", "presence" or "location". Defaults to "movement". For a detailed description of
            this argument, please refer to the docstring in ``calculate_pitch_control_difference``.

        :param float alpha: alpha (transparency) of player markers. Default is 0.7
        :param float alpha_pitch_control: alpha (transparency) of spaces heatmap. Default is 0.5
        :param dict team_color_dict:


        Returns:
            This function technically does not return anything, but does produce a matplotlib plot.
        """
        (
            pitch_control_difference,
            xgrid,
            ygrid,
        ) = self.calculate_pitch_control_difference(
            replace_x_velocity=replace_x_velocity,
            replace_y_velocity=replace_y_velocity,
            relative_x_change=relative_x_change,
            relative_y_change=relative_y_change,
            replace_function=replace_function,
            replace_velocity=replace_velocity,
        )

        if replace_function == "presence":
            fig, ax = mviz.plot_pitchcontrol_for_event(
                event_id=self.event_id,
                events=self.events,
                df_dict=self.df_dict,
                PPCF=pitch_control_difference,
                annotate=True,
                xgrid=xgrid,
                ygrid=ygrid,
                plotting_presence=True,
                team_to_plot=self.team_player_to_analyze,
                alpha=alpha,
                alpha_pitch_control=alpha_pitch_control,
                team_color_dict=team_color_dict,
            )
        elif replace_function == "movement":

            fig, ax = mviz.plot_pitchcontrol_for_event(
                event_id=self.event_id,
                events=self.events,
                df_dict=self.df_dict,
                PPCF=pitch_control_difference,
                annotate=True,
                xgrid=xgrid,
                ygrid=ygrid,
                plotting_difference=True,
                alpha=alpha,
                alpha_pitch_control=alpha_pitch_control,
                team_color_dict=team_color_dict,
            )
        elif replace_function == "location":
            event_frame = self.events.loc[self.event_id]["Start Frame"]
            x_coordinate = (
                self.df_dict[self.team_player_to_analyze].loc[event_frame][
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_x"
                ]
                + relative_x_change
            )
            y_coordinate = (
                self.df_dict[self.team_player_to_analyze].loc[event_frame][
                    f"{self.team_player_to_analyze}_{self.player_to_analyze}_y"
                ]
                + relative_y_change
            )
            if not replace_velocity:
                replace_x_velocity = self.df_dict[self.team_player_to_analyze].loc[
                    event_frame
                ][f"{self.team_player_to_analyze}_{self.player_to_analyze}_vx"]
                replace_y_velocity = self.df_dict[self.team_player_to_analyze].loc[
                    event_frame
                ][f"{self.team_player_to_analyze}_{self.player_to_analyze}_vy"]

            fig, ax = mviz.plot_pitchcontrol_for_event(
                event_id=self.event_id,
                events=self.events,
                df_dict=self.df_dict,
                PPCF=pitch_control_difference,
                annotate=True,
                xgrid=xgrid,
                ygrid=ygrid,
                plotting_new_location=True,
                plotting_difference=True,
                player_id=self.player_to_analyze,
                player_x_coordinate=x_coordinate,
                player_y_coordinate=y_coordinate,
                player_x_velocity=replace_x_velocity,
                player_y_velocity=replace_y_velocity,
                alpha=alpha,
                alpha_pitch_control=alpha_pitch_control,
                team_color_dict=team_color_dict,
            )
        if replace_function == "movement":
            plt.title(
                "Space created by "
                + str(self.team_player_to_analyze)
                + " Player "
                + str(self.player_to_analyze)
                + " during event "
                + str(self.event_id),
                fontdict={"fontsize": 18},
            )
        elif replace_function == "presence":
            plt.title(
                "Space occupied by "
                + str(self.team_player_to_analyze)
                + " Player "
                + str(self.player_to_analyze)
                + " during event "
                + str(self.event_id),
                fontdict={"fontsize": 18},
            )
        elif replace_function == "location":
            plt.title(
                "Difference In Pitch Control After Moving "
                + str(self.team_player_to_analyze)
                + " Player "
                + str(self.player_to_analyze),
                fontdict={"fontsize": 18},
            )

        return fig, ax

    def _get_players_on_pitch(self):
        pass_frame = self.events.loc[self.event_id]["Start Frame"]
        players_on_pitch = []

        data_row = self.df_dict[self.team_player_to_analyze].loc[pass_frame]

        for index in data_row.index:
            if "_vx" in index:
                if not np.isnan(data_row.loc[index]):
                    players_on_pitch.append(index.split("_")[1])
        return players_on_pitch

    def _validate_inputs(self):
        if type(self.player_to_analyze) not in (str, int):
            raise ValueError("player_to_analyze must be an integer or a string")

        if self.team_player_to_analyze not in list(self.df_dict.keys()):
            raise ValueError(
                f"team_player_to_analyze must equal {list(self.df_dict.keys())}"
            )

        if str(self.player_to_analyze) not in self._get_players_on_pitch():
            raise ValueError(
                "player_to_analyze is either not on the correct team, or was not on the pitch at the time of the event"
            )
