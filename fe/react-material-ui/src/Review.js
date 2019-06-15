import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';

var request = require('sync-request');

const products = [
  { name: 'Product 1', desc: 'A nice thing', price: '$9.99' },
  { name: 'Product 2', desc: 'Another thing', price: '$3.45' },
  { name: 'Product 3', desc: 'Something else', price: '$6.51' },
  { name: 'Product 4', desc: 'Best thing of all', price: '$14.11' },
  { name: 'Shipping', desc: '', price: 'Free' },
];
const addresses = ['1 Material-UI Drive', 'Reactville', 'Anytown', '99999', 'USA'];
const payments = [
  { name: 'Card type', detail: 'Visa' },
  { name: 'Card holder', detail: 'Mr John Smith' },
  { name: 'Card number', detail: 'xxxx-xxxx-xxxx-1234' },
  { name: 'Expiry date', detail: '04/2024' },
];

const useStyles = makeStyles(theme => ({
  listItem: {
    padding: theme.spacing(1, 0),
  },
  total: {
    fontWeight: '700',
  },
  title: {
    marginTop: theme.spacing(2),
  },
}));

class Review extends React.Component {
  constructor(props) {
    super(props);
    var a = JSON.parse(request('GET', 'http://127.0.0.1:5000/fcm/concepts').getBody('utf8'))
    this.state = {
      concs: a['data']['list'],
      weights: {}
    }
  }

  render() {
    return (
      <React.Fragment>
        <Typography variant="h6" gutterBottom>
          Значения весов концептов:

          {
            this.state['concs'].map(conc => (
              <TextField id={conc} name={conc} label={conc} fullWidth placeholder='0'
                onChange={
                  (obj) => {
                    console.log(this.state);
                    this.state['weights'][conc] = obj.target.value;
                    this.setState(this.state);
                    this.props.weightsCB(this.state['weights'])
                  }
                }
              />
            ))
          }

        </Typography>
      </React.Fragment>
    );
  }
}

export default Review;