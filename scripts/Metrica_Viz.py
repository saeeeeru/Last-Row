#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 09:10:58 2020

Module for visualising Metrica tracking and event data

Data can be found at: https://github.com/metrica-sports/sample-data

@author: Laurie Shaw (@EightyFivePoint)
The majority of code in this file can be found from the following Github repo:
https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

twitter_color = "#141d26"

def plot_pitch( field_dimen = (106.0,68.0), field_color ='green', linewidth=2, markersize=20):
    """ plot_pitch
    
    Plots a soccer pitch. All distance units converted to meters.
    
    Parameters
    -----------
        field_dimen: (length, width) of field in meters. Default is (106,68)
        field_color: color of field. options are {'green','white'}
        linewidth  : width of lines. default = 2
        markersize : size of markers (e.g. penalty spot, centre spot, posts). default = 20
        
    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)

    """
    fig,ax = plt.subplots(figsize=(12,8)) # create a figure 
    # decide what color we want the field to be. Default is green, but can also choose white
    if field_color=='green':
        ax.set_facecolor('mediumseagreen')
        fig.patch.set_facecolor('mediumseagreen')
        lc = 'whitesmoke' # line color
        pc = 'w' # 'spot' colors
    elif field_color=='white':
        lc = 'k'
        pc = 'k'
    elif field_color=='twitter_dark_mode':
        ax.set_facecolor(twitter_color)
        fig.patch.set_facecolor(twitter_color)
        lc = 'whitesmoke'
        pc = 'w'
    else:
        print(f'{field_color} does not exist in setting...')
        exit()

    # ALL DIMENSIONS IN m
    border_dimen = (3,3) # include a border arround of the field of width 3m
    meters_per_yard = 0.9144 # unit conversion from yards to meters
    half_pitch_length = field_dimen[0]/2. # length of half pitch
    half_pitch_width = field_dimen[1]/2. # width of half pitch
    signs = [-1,1] 
    # Soccer field dimensions typically defined in yards, so we need to convert to meters
    goal_line_width = 8*meters_per_yard
    box_width = 20*meters_per_yard
    box_length = 6*meters_per_yard
    area_width = 44*meters_per_yard
    area_length = 18*meters_per_yard
    penalty_spot = 12*meters_per_yard
    corner_radius = 1*meters_per_yard
    D_length = 8*meters_per_yard
    D_radius = 10*meters_per_yard
    D_pos = 12*meters_per_yard
    centre_circle_radius = 10*meters_per_yard
    # plot half way line # center circle
    ax.plot([0,0],[-half_pitch_width,half_pitch_width],lc,linewidth=linewidth)
    ax.scatter(0.0,0.0,marker='o',facecolor=lc,linewidth=0,s=markersize)
    y = np.linspace(-1,1,50)*centre_circle_radius
    x = np.sqrt(centre_circle_radius**2-y**2)
    ax.plot(x,y,lc,linewidth=linewidth)
    ax.plot(-x,y,lc,linewidth=linewidth)
    for s in signs: # plots each line seperately
        # plot pitch boundary
        ax.plot([-half_pitch_length,half_pitch_length],[s*half_pitch_width,s*half_pitch_width],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length,s*half_pitch_length],[-half_pitch_width,half_pitch_width],lc,linewidth=linewidth)
        # goal posts & line
        ax.plot( [s*half_pitch_length,s*half_pitch_length],[-goal_line_width/2.,goal_line_width/2.],pc+'s',markersize=6*markersize/20.,linewidth=linewidth)
        # 6 yard box
        ax.plot([s*half_pitch_length,s*half_pitch_length-s*box_length],[box_width/2.,box_width/2.],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length,s*half_pitch_length-s*box_length],[-box_width/2.,-box_width/2.],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length-s*box_length,s*half_pitch_length-s*box_length],[-box_width/2.,box_width/2.],lc,linewidth=linewidth)
        # penalty area
        ax.plot([s*half_pitch_length,s*half_pitch_length-s*area_length],[area_width/2.,area_width/2.],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length,s*half_pitch_length-s*area_length],[-area_width/2.,-area_width/2.],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length-s*area_length,s*half_pitch_length-s*area_length],[-area_width/2.,area_width/2.],lc,linewidth=linewidth)
        # penalty spot
        ax.scatter(s*half_pitch_length-s*penalty_spot,0.0,marker='o',facecolor=lc,linewidth=0,s=markersize)
        # corner flags
        y = np.linspace(0,1,50)*corner_radius
        x = np.sqrt(corner_radius**2-y**2)
        ax.plot(s*half_pitch_length-s*x,-half_pitch_width+y,lc,linewidth=linewidth)
        ax.plot(s*half_pitch_length-s*x,half_pitch_width-y,lc,linewidth=linewidth)
        # draw the D
        y = np.linspace(-1,1,50)*D_length # D_length is the chord of the circle that defines the D
        x = np.sqrt(D_radius**2-y**2)+D_pos
        ax.plot(s*half_pitch_length-s*x,y,lc,linewidth=linewidth)
        
    # remove axis labels and ticks
    ax.spines['top'].set_visible(False); ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    # set axis limits
    xmax = field_dimen[0]/2. + border_dimen[0]
    ymax = field_dimen[1]/2. + border_dimen[1]
    ax.set_xlim([-xmax,xmax])
    ax.set_ylim([-ymax,ymax])
    ax.set_axisbelow(True)

    return fig,ax

def plot_frame(df_dict, figax=None, team_color_dict={'Home':'r','Away':'b'}, field_dimen = (106.0,68.0), include_player_velocities=False, PlayerMarkerSize=10, PlayerAlpha=0.7, annotate=False ):
    """ plot_frame( hometeam, awayteam )
    
    Plots a frame of Metrica tracking data (player positions and the ball) on a football pitch. All distances should be in meters.
    
    Parameters
    -----------
        df_dict:
        fig,ax: Can be used to pass in the (fig,ax) objects of a previously generated pitch. Set to (fig,ax) to use an existing figure, or None (the default) to generate a new pitch plot, 
        team_color_dict: 
        field_dimen: tuple containing the length and width of the pitch in meters. Default is (106,68)
        include_player_velocities: Boolean variable that determines whether player velocities are also plotted (as quivers). Default is False
        PlayerMarkerSize: size of the individual player marlers. Default is 10
        PlayerAlpha: alpha (transparency) of player markers. Defaault is 0.7
        annotate: Boolean variable that determines with player jersey numbers are added to the plot (default is False)
        
    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)

    """
    if figax is None: # create new pitch 
        fig,ax = plot_pitch( field_dimen = field_dimen )
    else: # overlay on a previously generated pitch
        fig,ax = figax # unpack tuple
    # plot home & away teams in order
    for team_name in df_dict.keys():
        team, color = df_dict[team_name], team_color_dict[team_name]
        x_columns = [c for c in team.keys() if c[-2:].lower()=='_x' and c!='ball_x'] # column header for player x positions
        y_columns = [c for c in team.keys() if c[-2:].lower()=='_y' and c!='ball_y'] # column header for player y positions
        ax.plot( team[x_columns], team[y_columns], color=color, marker='o', MarkerSize=PlayerMarkerSize, linestyle='None', alpha=PlayerAlpha ) # plot player positions
        if include_player_velocities:
            vx_columns = ['{}_vx'.format(c[:-2]) for c in x_columns] # column header for player x positions
            vy_columns = ['{}_vy'.format(c[:-2]) for c in y_columns] # column header for player y positions
            ax.quiver( team[x_columns], team[y_columns], team[vx_columns], team[vy_columns], color=color, scale_units='inches', scale=10.,width=0.0015,headlength=5,headwidth=3,alpha=PlayerAlpha)
        if annotate:
            [ax.text( team[x]+0.5, team[y]+0.5, x.split('_')[1], fontsize=10, color=color) for x,y in zip(x_columns,y_columns) if not (np.isnan(team[x]) or np.isnan(team[y]))] 
    # plot ball
    team_name = list(df_dict.keys())[0]
    ax.plot(df_dict[team_name]['ball_x'], df_dict[team_name]['ball_y'], color='yellow', marker='o', MarkerSize=6, alpha=1.0, LineWidth=0)
    # set legend
    ax.legend(handles=[mpatches.Patch(color=color, label=team_name) for team_name, color in team_color_dict.items()], fontsize=12, title='Team')
    return fig,ax
    
def save_match_clip(df_dict, fpath, fname='clip_test', figax=None, frames_per_second=25, team_color_dict={'Home':'r','Away':'b'}, field_dimen = (106.0,68.0), annotate=False, include_player_velocities=False, PlayerMarkerSize=10, PlayerAlpha=0.7):
    """ save_match_clip( hometeam, awayteam, fpath )
    
    Generates a movie from Metrica tracking data, saving it in the 'fpath' directory with name 'fname'
    
    Parameters
    -----------
        df_dict: 
        fpath: directory to save the movie
        fname: movie filename. Default is 'clip_test.mp4'
        fig,ax: Can be used to pass in the (fig,ax) objects of a previously generated pitch. Set to (fig,ax) to use an existing figure, or None (the default) to generate a new pitch plot,
        frames_per_second: frames per second to assume when generating the movie. Default is 25.
        team_color_dict:
        field_dimen: tuple containing the length and width of the pitch in meters. Default is (106,68)
        annotate: Boolen
        include_player_velocities: Boolean variable that determines whether player velocities are also plotted (as quivers). Default is False
        PlayerMarkerSize: size of the individual player marlers. Default is 10
        PlayerAlpha: alpha (transparency) of player markers. Defaault is 0.7
        
    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)

    """
    # check that indices match first
    team1, team2 = list(df_dict.keys())
    assert np.all( df_dict[team1].index==df_dict[team2].index ), "Home and away team Dataframe indices must be the same"
    # in which case use home team index
    index = df_dict[team1].index
    # Set figure and movie settings
    FFMpegWriter = animation.writers['ffmpeg']
    metadata = dict(title='Tracking Data', artist='Matplotlib', comment='Metrica tracking data clip')
    writer = FFMpegWriter(fps=frames_per_second, metadata=metadata)
    fname = fpath + '/' +  fname + '.mp4' # path and filename
    # create football pitch
    if figax is None:
        fig,ax = plot_pitch(field_dimen=field_dimen)
    else:
        fig,ax = figax
    fig.set_tight_layout(True)
    # Generate movie
    print("Generating movie...",end='')
    with writer.saving(fig, fname, 100):
        for i in index:
            figobjs = [] # this is used to collect up all the axis objects so that they can be deleted after each iteration
            for team_name in df_dict.keys():
                team = df_dict[team_name].loc[i]
                color = team_color_dict[team_name]
                x_columns = [c for c in team.keys() if c[-2:].lower()=='_x' and c!='ball_x'] # column header for player x positions
                y_columns = [c for c in team.keys() if c[-2:].lower()=='_y' and c!='ball_y'] # column header for player y positions
                objs, = ax.plot( team[x_columns], team[y_columns], color=color, linestyle='None', marker='o', MarkerSize=PlayerMarkerSize, alpha=PlayerAlpha ) # plot player positions
                figobjs.append(objs)
                if include_player_velocities:
                    vx_columns = ['{}_vx'.format(c[:-2]) for c in x_columns] # column header for player x positions
                    vy_columns = ['{}_vy'.format(c[:-2]) for c in y_columns] # column header for player y positions
                    objs = ax.quiver( team[x_columns], team[y_columns], team[vx_columns], team[vy_columns], color=color, scale_units='inches', scale=10.,width=0.0015,headlength=5,headwidth=3,alpha=PlayerAlpha)
                    figobjs.append(objs)
                if annotate:
                    figobjs += [ax.text( team[x]+0.5, team[y]+0.5, x.split('_')[0], fontsize=10, color=color) for x,y in zip(x_columns,y_columns) if not (np.isnan(team[x]) or np.isnan(team[y]))]
            # plot ball
            objs, = ax.plot( team['ball_x'], team['ball_y'], color='yellow', marker='o', MarkerSize=6, alpha=1.0, LineWidth=0)
            figobjs.append(objs)
            # include match time at the top
            frame_minute =  int( team['Time [s]']/60. )
            frame_second =  ( team['Time [s]']/60. - frame_minute ) * 60.
            timestring = "%d:%1.2f" % ( frame_minute, frame_second  )
            objs = ax.text(-2.5,field_dimen[1]/2.+1., timestring, fontsize=14, color='w')
            figobjs.append(objs)
            # set legend
            figobjs.append(ax.legend(handles=[mpatches.Patch(color=color, label=team_name) for team_name, color in team_color_dict.items()], fontsize=12, title='Team'))
            writer.grab_frame()
            # Delete all axis objects (other than pitch lines) in preperation for next frame
            for figobj in figobjs:
                figobj.remove()
    print("done")
    plt.clf()
    plt.close(fig)    


def plot_events( events, figax=None, field_dimen = (106.0,68), indicators = ['Marker','Arrow'], color='r', marker_style = 'o', alpha = 0.5, annotate=False):
    """ plot_events( events )
    
    Plots Metrica event positions on a football pitch. event data can be a single or several rows of a data frame. All distances should be in meters.
    
    Parameters
    -----------
        events: row (i.e. instant) of the home team tracking data frame
        fig,ax: Can be used to pass in the (fig,ax) objects of a previously generated pitch. Set to (fig,ax) to use an existing figure, or None (the default) to generate a new pitch plot, 
        field_dimen: tuple containing the length and width of the pitch in meters. Default is (106,68)
        indicators: List containing choices on how to plot the event. 'Marker' places a marker at the 'Start X/Y' location of the event; 'Arrow' draws an arrow from the start to end locations. Can choose one or both.
        color: color of indicator. Default is 'r' (red)
        marker_style: Marker type used to indicate the event position. Default is 'o' (filled ircle).
        alpha: alpha of event marker. Default is 0.5    
        annotate: Boolean determining whether text annotation from event data 'Type' and 'From' fields is shown on plot. Default is False.
        
    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)

    """

    if figax is None: # create new pitch 
        fig,ax = plot_pitch( field_dimen = field_dimen )
    else: # overlay on a previously generated pitch
        fig,ax = figax 
    for i,row in events.iterrows():
        if 'Marker' in indicators:
            ax.plot(  row['Start X'], row['Start Y'], color=color, marker=marker_style, alpha=alpha)
        if 'Arrow' in indicators:
            ax.annotate("", xy=row[['End X','End Y']], xytext=row[['Start X','Start Y']], alpha=alpha, arrowprops=dict(alpha=alpha,arrowstyle="->",color=color),annotation_clip=False)
        if annotate:
            textstring = row['Type'] + ': ' + row['From']
            ax.text( row['Start X'], row['Start Y'], textstring, fontsize=10, color=color)
    return fig,ax

# This function is modified from @EightyFivePoint's adaptation. However, there are no breaking changes,
# so the original syntax/arguments are still valid
def plot_pitchcontrol_for_event(
    event_id,
    events,
    df_dict,
    PPCF,
    xgrid,
    ygrid,
    alpha=0.7,
    include_player_velocities=True,
    annotate=False,
    field_dimen=(106.0, 68),
    plotting_difference=False,
    plotting_presence=False,
    plotting_new_location=False,
    team_to_plot="Home",
    player_x_coordinate=None,
    player_y_coordinate=None,
    player_id=0,
    player_x_velocity=0,
    player_y_velocity=0,
    alpha_pitch_control=0.5,
    team_color_dict={'Home':"r", 'Away':"b"},
    field_color="white"
):
    """ plot_pitchcontrol_for_event( event_id, events,  tracking_home, tracking_away, PPCF, xgrid, ygrid )

    Plots the pitch control surface at the instant of the event given by the event_id. Player and ball positions are overlaid.

    Parameters
    -----------
        event_id: Index (not row) of the event that describes the instant at which the pitch control surface should be calculated
        events: Dataframe containing the event data
        df_dict: keys=team, values=pd.DataFrame
        PPCF: Pitch control surface (dimen (n_grid_cells_x,n_grid_cells_y) ) containing pitch control probability for the attcking team (as returned by the generate_pitch_control_for_event in Metrica_PitchControl)
        xgrid: Positions of the pixels in the x-direction (field length) as returned by the generate_pitch_control_for_event in Metrica_PitchControl
        ygrid: Positions of the pixels in the y-direction (field width) as returned by the generate_pitch_control_for_event in Metrica_PitchControl
        alpha: alpha (transparency) of player markers. Default is 0.7
        include_player_velocities: Boolean variable that determines whether player velocities are also plotted (as quivers). Default is False
        annotate: Boolean variable that determines with player jersey numbers are added to the plot (default is False)
        field_dimen: tuple containing the length and width of the pitch in meters. Default is (106,68)
        plotting_difference: Tells us if we are plotting a difference of pitch controls
        alpha_pitch_control: alpha (transparency) of spaces heatmap. Default is 0.5
        team_color_dict: 
        field_color: color of the field. Default is green.

    Returrns
    -----------
       fig,ax : figure and axis objects (so that other data can be plotted onto the pitch)

    """

    # pick a pass at which to generate the pitch control surface
    event_frame = events.loc[event_id]["Start Frame"]

    possession_team = events.loc[event_id].Team
    cmap = LinearSegmentedColormap.from_list("", [color for team, color in team_color_dict.items() if team != possession_team] + ["white", team_color_dict[possession_team]])

    tmp_df_dict = {team:df.loc[event_frame] for team, df in df_dict.items()}

    # plot frame and event
    fig, ax = plot_pitch(field_color=field_color, field_dimen=field_dimen)
    plot_frame(
        tmp_df_dict,
        figax=(fig, ax),
        team_color_dict=team_color_dict,
        PlayerAlpha=alpha,
        include_player_velocities=include_player_velocities,
        annotate=annotate,
    )
    plot_events(
        events.loc[event_id:event_id],
        figax=(fig, ax),
        indicators=["Marker", "Arrow"],
        annotate=False,
        color="k",
        alpha=1,
    )
    # If we want to add a new player, plot a new player on the pitch
    if plotting_new_location:
        print("Plotting new location")
        plot_new_player(
            player_x_coordinate=player_x_coordinate,
            player_y_coordinate=player_y_coordinate,
            player_x_velocity=player_x_velocity,
            player_y_velocity=player_y_velocity,
            figax=(fig, ax),
            PlayerAlpha=alpha,
            include_player_velocities=include_player_velocities,
            annotate=annotate,
            player_id=player_id,
        )
        PPCF = -1 * PPCF

    # If we need to apply a transformation to ensure the 0 points are white, apply the transformation
    if plotting_difference:
        PPCF = convert_pitch_control_for_cmap(PPCF)

    # plot pitch control surface
    ax.imshow(
        np.flipud(PPCF),
        extent=(np.amin(xgrid), np.amax(xgrid), np.amin(ygrid), np.amax(ygrid)),
        interpolation="lanczos",
        vmin=0.0,
        vmax=1.0,
        alpha=alpha_pitch_control,
        cmap=cmap,
    )
    return fig, ax


def plot_new_player(
    player_x_coordinate,
    player_y_coordinate,
    player_x_velocity,
    player_y_velocity,
    player_id,
    color="g",
    figax=None,
    include_player_velocities=False,
    PlayerMarkerSize=12,
    PlayerAlpha=0.7,
    annotate=False,
):
    """
    Function description:
        This function allows us to overlay a new location for a player, along with a velocity vector on top of an
        existing surface. The code uses the same logic as ``plot_frame``, but is altered to incorporate only adding
        one new player.

    Input parameters:
    :param float player_x_coordinate: x coordinate of the new player's location
    :param float player_y_coordinate: y coordinate of the new player's location
    :param float player_x_velocity: x component of the new player's velocity vector
    :param float player_y_velocity: y component of the new player's velocity vector
    :param int player_id: ID number of the new player
    :param string color: Color to
    :param fig,ax: Can be used to pass in the (fig,ax) objects of a previously generated pitch. Set to (fig,ax) to use
        an existing figure, or None (the default) to generate a new pitch plot.
    The remainder of the parameters are inherited from either ``plot_event`` or ``plot_frame``

    Returns:
    fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)

    """
    fig, ax = figax  # unpack tuple
    # Plot New Player

    ax.plot(
        player_x_coordinate,
        player_y_coordinate,
        color=color,
        marker="o",
        MarkerSize=PlayerMarkerSize,
        alpha=PlayerAlpha,
    )
    if include_player_velocities:
        ax.quiver(
            player_x_coordinate,
            player_y_coordinate,
            player_x_velocity,
            player_y_velocity,
            color=color,
            alpha=PlayerAlpha,
            scale_units="inches",
            scale=10.0,
            width=0.0015,
            headlength=5,
            headwidth=3,
        )
    if annotate:
        ax.text(
            player_x_coordinate + 0.6,
            player_y_coordinate + 0.6,
            str(player_id),
            fontsize=12,
            color=color,
        )
    return fig, ax


def convert_pitch_control_for_cmap(pitch_control):
    """
    Function Description:
    This function converts a pitch control surface with negative values to a surface that can be used appropriately
    with a cmap. The issue was that we need the minimum value to map to 0, the maximum value to map  to 0.5, and the
    maximum value to map to 1 in order for the plot to plot the unaffected areas of the pitch white. The transformations
    done in this function are the solutions of a system of equations to map these 3 values to their desired targets.

    There is likely a better solution to this problem than what is done here, so I am open to reviewing pull requests to
    improve this. Currently, the main flaw of this solution is that the intensity of the colors can be misleading.
    If the min value is -0.1 while the max value is 0.9, the min and max values will still be displayed with the same
    intensity due to this transformation. Thus, I don't recommended plotting the off ball movement of players who are
    barely moving during the event until a better solution can be reached.

    Input parameters:
    :param pitch_control: An ndarray that represents the difference between two pitch control arrays

    Returns:
    :return: An adjusted surface to be passed into ``plot_pitch_control_for_event``
    """
    min_value = pitch_control.min()
    max_value = pitch_control.max()
    quadratic_coef = (
        0.5
        * (min_value + max_value)
        / ((max_value * min_value) * (max_value - min_value))
    )
    linear_coef = (
        0.5
        * (min_value ** 2 + max_value ** 2)
        / ((min_value * max_value) * max_value * min_value)
    )
    constant_term = 0.5
    quadratic_array = quadratic_coef * np.square(pitch_control)
    linear_array = linear_coef * pitch_control
    constant_array = constant_term + 0 * pitch_control
    return quadratic_array + linear_array + constant_array
