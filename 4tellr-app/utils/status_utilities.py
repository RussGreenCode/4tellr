

class StatusUtilities:
    @staticmethod
    def get_plot_status(plot_type, outcome_status):
        if outcome_status == 'ON_TIME':
            return 'MET_THRESHOLD'
        elif outcome_status == 'MEETS_SLO':
            if plot_type == 'EXP':
                return 'BREACHED'
            else:
                return 'MET_THRESHOLD'
        elif outcome_status == 'MEETS_SLA':
            if plot_type == 'SLA':
                return 'MET_THRESHOLD'
            else:
                return 'BREACHED'
        else:
            return 'BREACHED'