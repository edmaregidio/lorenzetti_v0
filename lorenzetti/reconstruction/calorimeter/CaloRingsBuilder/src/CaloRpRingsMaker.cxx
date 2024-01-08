

#include "CaloRpRingsMaker.h"
#include "CaloCell/CaloCell.h"
#include "CaloCluster/CaloCluster.h"
#include "G4Kernel/CaloPhiRange.h"
#include "TH1F.h"
#include "TH2F.h"
#include <numeric>

using namespace SG;
using namespace Gaugi;


CaloRpRingsMaker::CaloRpRingsMaker( std::string name ) : 
  IMsgService(name),
  Algorithm()
{
  declareProperty( "RingerKey"      , m_ringerKey="RpRings"     );
  declareProperty( "ClusterKey"     , m_clusterKey="Clusters" );
  declareProperty( "DeltaEtaRings"  , m_detaRings={}          );
  declareProperty( "DeltaPhiRings"  , m_dphiRings={}          );
  declareProperty( "NRings"         , m_nRings={}             );
  declareProperty( "LayerRings"     , m_layerRings={}         );
  declareProperty( "OutputLevel"    , m_outputLevel=1         );
  declareProperty( "HistogramPath"  , m_histPath=""           );
  declareProperty( "Alpha"          , m_alpha                 );
  declareProperty( "Beta"           , m_beta                  );
  declareProperty( "RpInit"         , m_rpInit={}             );
}

//!=====================================================================

CaloRpRingsMaker::~CaloRpRingsMaker()
{;}

//!=====================================================================

StatusCode CaloRpRingsMaker::initialize()
{
  CHECK_INIT();

  setMsgLevel(m_outputLevel);
  m_maxRingsAccumulated = std::accumulate(m_nRings.begin(), m_nRings.end(), 0);
  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode CaloRpRingsMaker::finalize()
{
  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode CaloRpRingsMaker::bookHistograms( EventContext &ctx ) const
{
  auto store = ctx.getStoreGateSvc();
  store->mkdir( m_histPath );
  store->add( new TH2F( "rprings", "Et Vs #rpring; #rpring; R_{P} Amplitude; Count", m_maxRingsAccumulated, 0, m_maxRingsAccumulated, 150, 0, 5 ));
  return StatusCode::SUCCESS;
}

//!=====================================================================


StatusCode CaloRpRingsMaker::pre_execute( EventContext &/*ctx*/ ) const
{
  return StatusCode::SUCCESS;
}

//!=====================================================================


StatusCode CaloRpRingsMaker::execute( EventContext &/*ctx*/, const G4Step * /*step*/ ) const
{
  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode CaloRpRingsMaker::execute( EventContext &ctx, int /*evt*/ ) const
{
  return post_execute(ctx);
}

//!=====================================================================

StatusCode CaloRpRingsMaker::post_execute( EventContext &ctx ) const
{

  
  SG::WriteHandle<xAOD::CaloRingsContainer> rpringer(m_ringerKey, ctx);
  rpringer.record( std::unique_ptr<xAOD::CaloRingsContainer>(new xAOD::CaloRingsContainer()) );

  SG::ReadHandle<xAOD::CaloClusterContainer> clusters(m_clusterKey, ctx);
  
  std::vector< RpRingSet > vec_rs;

  for ( int rs=0 ; rs < (int)m_nRings.size(); ++rs )
  {  
    std::vector<CaloSampling> samplings;
    for(auto samp : m_layerRings[rs])  {
      samplings.push_back((CaloSampling)samp);
    }
    vec_rs.push_back( RpRingSet( samplings, m_nRings[rs], m_detaRings[rs], m_dphiRings[rs], m_rpInit[rs]) );
  }

  // Loop over all CaloClusters
  for( auto* clus : **clusters.ptr())
  {
    MSG_DEBUG( "Creating the CaloRings for this cluster..." );
    // Create the CaloRings object
    auto rprings = new xAOD::CaloRings();

    for ( auto &rs : vec_rs ){

      // zeroize
      rs.clear();

      auto *hotCell = maxCell( clus, rs );
     
      // Fill all rings using the hottest cell as center
      
      for ( auto* cell : clus->cells() )
      { 
        float rp_value = 0;
        if (hotCell){
          
          rp_value = rs.computeRp(clus, cell, hotCell->eta(), hotCell->phi(),m_alpha, m_beta);  
          rs.push_back( cell, hotCell->eta(), hotCell->phi(), rp_value );
        }else{
        
          rp_value = rs.computeRp(clus, cell, clus->eta(), clus->phi(),m_alpha, m_beta);  
          rs.push_back( cell, clus->eta(), clus->phi(), rp_value );
        }
      }
      
    }

    std::vector<float> ref_rings;
    ref_rings.reserve( m_maxRingsAccumulated );

    for ( auto& rs : vec_rs )
      ref_rings.insert(ref_rings.end(), rs.rings().begin(), rs.rings().end());

    MSG_DEBUG( "Setting all ring informations and attach into the EventContext." );
    rprings->setRings( ref_rings );
    rprings->setCaloCluster( clus );
    rpringer->push_back( rprings );

  }
  
  return StatusCode::SUCCESS;
}

//!=====================================================================

const xAOD::CaloCell * CaloRpRingsMaker::maxCell( const xAOD::CaloCluster *clus, RpRingSet &rs ) const
{
  const xAOD::CaloCell *maxCell=nullptr;

  for ( auto *cell : clus->cells() ){

    if( !rs.isValid(cell) ) continue;

    if(!maxCell)  maxCell=cell;

    if (cell->e() > maxCell->e() )
        maxCell = cell;
  }// Loop over all cells inside of this cluster
  return maxCell;
}

//!=====================================================================

StatusCode CaloRpRingsMaker::fillHistograms( EventContext &ctx ) const
{
  auto store = ctx.getStoreGateSvc();
  SG::ReadHandle<xAOD::CaloRingsContainer> rpringer( m_ringerKey, ctx );

  if( !rpringer.isValid() ){
    MSG_ERROR( "It's not possible to read CaloRingsContainer from this Context using this key "<< m_ringerKey );
    return StatusCode::FAILURE;
  }

  store->cd(m_histPath);
  for (auto rprings : **rpringer.ptr() ){
    auto ringerShape = rprings->rings();

    for (int r=0; r < m_maxRingsAccumulated; ++r){
      store->hist1("rprings")->Fill( r, ringerShape.at(r) );
    }
  }

  return StatusCode::SUCCESS;
}

//!=====================================================================
//!=====================================================================
//!=====================================================================
//!=====================================================================


RpRingSet::RpRingSet( std::vector<CaloSampling> &samplings, unsigned nrings, float deta, float dphi, int rpinit  ):
  m_rings(nrings,0), 
  m_deta(deta), 
  m_dphi(dphi),
  m_samplings(samplings),
  m_rpinit(rpinit)
{;}

//!=====================================================================

void RpRingSet::push_back( const xAOD::CaloCell *cell , float eta_center, float phi_center, float rp )
{
  // This cell does not allow to this RingSet
  if( isValid(cell) ){
    float deta = std::abs( eta_center - cell->eta() ) / m_deta;
    float dphi = std::abs( CaloPhiRange::diff(phi_center , cell->phi()) ) / m_dphi;
    float deltaGreater = std::max(deta, dphi);
    int i = static_cast<unsigned int>( std::round(deltaGreater) );

    
    if( i < (int)m_rings.size() ){
      m_rings[i] += rp;
    }
  }
}

//!=====================================================================

double RpRingSet::computeRp( const xAOD::CaloCluster *clus, const xAOD::CaloCell *cell , float eta_center, float phi_center, float alpha, float beta)
{
  
  double den = 0;
  for ( auto* m_cell : clus->cells() ){
    if (!isValid(m_cell)) continue;
    float cell_e = m_cell->e() > 0 ? m_cell->e(): 1e-6;
    den += pow(cell_e/std::cosh(std::abs(cell->eta())),alpha);
  }
  if (isValid(cell)) {
    float deta = std::abs( eta_center - cell->eta() ) / m_deta;
    float dphi = std::abs( CaloPhiRange::diff(phi_center , cell->phi()) ) / m_dphi;
    float deltaGreater = std::max(deta, dphi);
    int rdist = static_cast<unsigned int>( std::floor(deltaGreater) );
    int index = rdist+m_rpinit+1;
    float r_beta = pow((index),beta);
    float cell_e = cell->e() > 0 ? cell->e(): 1e-6;
    double e_alpha = pow((cell_e/std::cosh(std::abs(cell->eta()))),alpha);
    double num = e_alpha * r_beta;
    return num/den;
  }
  else return -999;
}

//!=====================================================================

size_t RpRingSet::size() const
{
  return m_rings.size();
}

//!=====================================================================

const std::vector<float>& RpRingSet::rings() const
{
  return m_rings;
}

//!=====================================================================

bool RpRingSet::isValid(const xAOD::CaloCell* cell ) const
{
  for( auto samp : m_samplings){
    if(cell->descriptor()->sampling() == samp)
      return true;
  }
  return false;
}

//!=====================================================================

void RpRingSet::clear()
{
  for (std::vector<float>::iterator it = m_rings.begin(); it < m_rings.end(); it++)
  {
    *it=0.0;
  }
}

