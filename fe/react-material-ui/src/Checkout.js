import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Paper from '@material-ui/core/Paper';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Button from '@material-ui/core/Button';
import Link from '@material-ui/core/Link';
import Typography from '@material-ui/core/Typography';
import AddressForm from './AddressForm';
import PaymentForm from './PaymentForm';
import Review from './Review';

function MadeWithLove() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
    </Typography>
  );
}

const useStyles = makeStyles(theme => ({
  appBar: {
    position: 'relative',
  },
  layout: {
    width: 'auto',
    marginLeft: theme.spacing(2),
    marginRight: theme.spacing(2),
    [theme.breakpoints.up(600 + theme.spacing(2) * 2)]: {
      width: 600,
      marginLeft: 'auto',
      marginRight: 'auto',
    },
  },
  paper: {
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(3),
    padding: theme.spacing(2),
    [theme.breakpoints.up(600 + theme.spacing(3) * 2)]: {
      marginTop: theme.spacing(6),
      marginBottom: theme.spacing(6),
      padding: theme.spacing(3),
    },
  },
  stepper: {
    padding: theme.spacing(3, 0, 5),
  },
  buttons: {
    display: 'flex',
    justifyContent: 'flex-end',
  },
  button: {
    marginTop: theme.spacing(3),
    marginLeft: theme.spacing(1),
  },
}));

const steps = ['Выбор дат и ограничений', 'Определение весов концептов', 'Результат'];

export default function Checkout() {
  const classes = useStyles();
  const [activeStep, setActiveStep] = React.useState({step: 0, data :{}});

  const handleNext = () => {
    setActiveStep({step: activeStep.step + 1, data: activeStep.data});
  };

  const handleBack = () => {
    setActiveStep({step: activeStep.step - 1, data: activeStep.data});
  };

  const getStepContent = (state) => {
    switch (state.step) {
      case 0:
        return <AddressForm />;
      case 1:
        return <Review weightsCB={ (weights) => { setActiveStep({step: activeStep.step, data: weights}); } }/>;
      case 2:
        return <PaymentForm weights={state.data} />;
      default:
        throw new Error('Unknown step:'+state.step);
    }
  }

  return (
    <React.Fragment>
      <CssBaseline />
      <AppBar position="absolute" color="default" className={classes.appBar}>
        <Toolbar>
          <Typography variant="h6" color="inherit" noWrap>
            Расчет концептов для анализа экономической обстановки в Московской области
          </Typography>
        </Toolbar>
      </AppBar>
      <main className={classes.layout}>
        <Paper className={classes.paper}>
          <Typography component="h1" variant="h4" align="center">

          </Typography>
          <Stepper activeStep={activeStep.step} className={classes.stepper}>
            {steps.map(label => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          <React.Fragment>
            <React.Fragment>
              {getStepContent(activeStep)}
              <div className={classes.buttons}>
                {activeStep.step !== 0 && (
                  <Button onClick={handleBack} className={classes.button}>
                    Назад
                  </Button>
                )}
                { activeStep.step !== steps.length-1 && <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNext}
                    className={classes.button}
                  >
                    {activeStep.step === steps.length - 1 ? 'Сохранить' : 'Далее'}
                  </Button>
                }
              </div>
            </React.Fragment>
          </React.Fragment>
        </Paper>
        <MadeWithLove />
      </main>
    </React.Fragment>
  );
}
