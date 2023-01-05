from .models import Req, Oscmodel, Osrmodel, Srmodel, Slpmodel
from .forms import ReqForm, OscForm, OsrForm, SrForm, SlpForm, OSR_dlr, OSR_gri, OSR_psr

model_dict = {
    'OSC': Oscmodel,
    'LAB': Slpmodel,
    'RES': Srmodel,
    'OSR': Osrmodel,
    'REQ': Req,
}

form_dict = {
    'OSC': OscForm,
    'LAB': SlpForm,
    'RES': SrForm,
    'OSR': OsrForm,
    'REQ': ReqForm,
}

show_dict = {
    'OSC': 'events/show_osc.html',
    'LAB': 'events/show_slp.html',
    'RES': 'events/show_sr.html',
    'OSR': 'events/show_osr.html',
}

thtml_dict = {
    'OSR_dlr': OSR_dlr,
    'OSR_gri': OSR_gri,
    'OSR_psr': OSR_psr,
}
