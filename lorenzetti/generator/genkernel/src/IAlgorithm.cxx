
#include "GenKernel/IAlgorithm.h"
#include <cmath>

using namespace Gaugi;
using namespace generator;
static const double c_light = 2.99792458e+8; // m/s


IAlgorithm::IAlgorithm(IGenerator *gen):
  IMsgService(),
  PropertyService(),
  m_generator(gen)
{
  declareProperty( "OutputLevel" , m_outputLevel=0                                                         );
  declareProperty( "Sigma_t"     , m_sigma_t = 200 * 1e-12 /*pico seconds*/ * c_light /*m/s*/ * 1e+3 /*mm*/);
  declareProperty( "Trunc_t"     , m_trunc_t = 10 * 1e-9 /*nano seconds*/ * c_light /*m/s*/ * 1e+3 /*mm*/  );
  declareProperty( "Sigma_z"     , m_sigma_z = 56 /*milimiters*/                                           );
  declareProperty( "Trunc_z"     , m_trunc_z = 10 * 1e-9 /*nano seconds*/ * c_light /*m/s*/ * 1e+3 /*mm*/  );
  declareProperty( "Trunc_mu"    , m_trunc_mu = 300 );
}


int IAlgorithm::poisson(double nAvg) 
{
  // Random number.
  double rPoisson = m_generator->random_flat() * exp(nAvg);
  // Initialize.
  double rSum  = 0.;
  double rTerm = 1.;
  // Add to sum and check whether done.
  for (int i = 0; i < m_trunc_mu ; ) {
    rSum += rTerm;
    if (rSum > rPoisson) return i;
    // Evaluate next term.
    ++i;
    rTerm *= nAvg / i;
  }
  // Emergency return.
  return m_trunc_mu;
}


float IAlgorithm::sample_z() const{
  return trunc_centered_gauss(m_sigma_z, m_trunc_z);
}

float IAlgorithm::sample_t() const{
  return trunc_centered_gauss(m_sigma_t, m_trunc_t);
}

template <typename T> int sign(T val) {
    return (T(0) < val) - (val < T(0));
}

float IAlgorithm::trunc_centered_gauss(float sigma, float trunc) const
{
  auto ret = m_generator->random_gauss() * sigma;
  ret = (std::abs(ret)<trunc)?ret:(sign(ret)*trunc);
  return ret;
}

const std::string& IAlgorithm::name() const
{
  return getLogName();
}


