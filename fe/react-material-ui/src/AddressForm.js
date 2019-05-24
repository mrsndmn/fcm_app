import React from 'react';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';

export default function AddressForm() {
  return (
    <React.Fragment>
      <Typography variant="h6" gutterBottom>
        Выберете даты для расчета концептов
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            id="date_from"
            name="Date from"
            type="Date"
            fullWidth
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            id="date_to"
            name="date_to"
            // label="Last name"
            type="Date"
            fullWidth
            // autoComplete="lname"
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            required
            id="max_iters"
            name="max_iters"
            label="Maximum number of iterations"
            fullWidth
            autoComplete="billing address-line1"
            value='1000'
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            id="eps"
            name="eps"
            label="Eps"
            fullWidth
            autoComplete="billing address-line2"
            value='0.0001'
          />
        </Grid>
        {/* <Grid item xs={12}>
          <FormControlLabel
            control={<Checkbox color="secondary" name="saveAddress" value="yes" />}
            label="Use this address for payment details"
          />
        </Grid> */}
      </Grid>
    </React.Fragment>
  );
}
