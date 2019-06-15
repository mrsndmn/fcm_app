import React from 'react';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';

var request = require('sync-request');
var qs = require('qs');

class PaymentForm extends React.Component {
  constructor(props) {
    super(props);
    console.log("props in payment form:", props);
    var q = qs.stringify( {'weights': JSON.stringify(props['weights'])} )
    console.log(q)
    var a = JSON.parse(request('GET', 'http://127.0.0.1:5000/fcm/calculator?'+q ).getBody('utf8'))
    console.log(a)
    this.state = {
      imgs: a['data']
    }
  }

  render() {
    return (
      <React.Fragment>
        <Typography variant="h6" gutterBottom>
          {/* Когнитивная карта */}
          <Grid container spacing={3}>
            {
              this.state['imgs'].map(imagesrc => ( <img src={imagesrc}></img> ) )
            }
          </Grid>
        </Typography>
      </React.Fragment>
    );
  }
}

export default PaymentForm;
