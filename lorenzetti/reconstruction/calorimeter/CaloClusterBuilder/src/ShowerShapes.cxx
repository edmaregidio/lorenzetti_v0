
#include "CaloCluster/CaloCluster.h"
#include "G4Kernel/CaloPhiRange.h"
#include "ShowerShapes.h"
#include "G4PhysicalConstants.hh"
#include "G4SystemOfUnits.hh"

using namespace std;
using namespace SG;



ShowerShapes::ShowerShapes( std::string name ) : 
  IMsgService(name),
  AlgTool()
  {;}

//!=====================================================================

StatusCode ShowerShapes::initialize()
{
  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode ShowerShapes::finalize()
{
  return StatusCode::SUCCESS;
}

//!=====================================================================

StatusCode ShowerShapes::execute( SG::EventContext &/*ctx*/, Gaugi::EDM *edm ) const
{
  MSG_DEBUG("Calculate shower shapes for this cluster." );
  
  auto *clus = static_cast<xAOD::CaloCluster*>(edm);

  // Eratio for strip em layer (EM1, all cells must be EMB1 or EMEC1 sampling)
  auto em1Cells = clus->cells();
	em1Cells.erase(std::remove_if(em1Cells.begin(),em1Cells.end(),
                [](const xAOD::CaloCell* c){return (
                  (c->descriptor()->sampling() != CaloSampling::EMB1) &&
                  (c->descriptor()->sampling() != CaloSampling::EMEC1) );}),
                em1Cells.end());


  std::sort(em1Cells.begin(), em1Cells.end(),
            [](const xAOD::CaloCell* c1, const xAOD::CaloCell* c2){return c1->e() > c2->e();});

  
  
  float emaxs1  = (em1Cells.size()>=4)?(em1Cells[0]->e() + em1Cells[1]->e()):0;
  float e2tsts1 = (em1Cells.size()>=4)?(em1Cells[2]->e() + em1Cells[3]->e()):0;
  float eratio = (emaxs1 + e2tsts1)?((emaxs1 - e2tsts1)/(emaxs1 + e2tsts1)):0.;

 
  
  float e277 = sumEnergyEM( clus, 2, 7, 7 );
  float e233 = sumEnergyEM( clus, 2, 3, 3 );
  float e237 = sumEnergyEM( clus, 2, 3, 7 );
  float reta = e237/e277;
  float rphi = e233/e237;
  float e0 = sumEnergyEM( clus, 0 );
  float e1 = sumEnergyEM( clus, 1 );
  float e2 = sumEnergyEM( clus, 2 );
  float e3 = sumEnergyEM( clus, 3 );


  float ehad1 = sumEnergyHAD( clus, 0 );
  float ehad2 = sumEnergyHAD( clus, 1 );
  float ehad3 = sumEnergyHAD( clus, 2 );
    
  float weta2 = calculateWeta2(clus, 3, 5);

  float etot = e0+e1+e2+e3+ehad1+ehad2+ehad3;
  float emtot = e0+e1+e2+e3;
  // fraction of energy deposited in 1st sampling
  float f0 = e0 / emtot;
  float f1 = e1 / emtot;
  float f2 = e2 / emtot;
  float f3 = e3 / emtot;

  float rhad = (ehad1+ehad2+ehad3) / emtot;
  float rhad1 = (ehad1) / emtot;

  float rp0     = rpmapping(clus, 0, m_alpha, m_beta, m_kappa, m_gamma);
  float rp1     = rpmapping(clus, 1, m_alpha, m_beta, m_kappa, m_gamma);
  float rp2     = rpmapping(clus, 2, m_alpha, m_beta, m_kappa, m_gamma);
  float rp3     = rpmapping(clus, 3, m_alpha, m_beta, m_kappa, m_gamma);
  float rphad1  = rpmapping(clus, 4, m_alpha, m_beta, m_kappa, m_gamma);
  float rphad2  = rpmapping(clus, 5, m_alpha, m_beta, m_kappa, m_gamma);
  float rphad3  = rpmapping(clus, 6, m_alpha, m_beta, m_kappa, m_gamma);
  
  clus->setE0( e0 );
  clus->setE1( e1 );
  clus->setE2( e2 );
  clus->setE3( e3 );
  clus->setEhad1( ehad1 );
  clus->setEhad2( ehad2 );
  clus->setEhad3( ehad3 );
  clus->setEtot( etot );
  clus->setE277( e277 );
  clus->setE237( e237 );
  clus->setE233( e233 );
  clus->setReta( reta );
  clus->setRphi( rphi );
  clus->setWeta2( weta2 );
  // Eratio for strip em layer (EM1)
  clus->setEratio( eratio );
  // Extra eratio information for each sampling layer
  clus->setEmaxs1( emaxs1 );
  clus->setE2tsts1( e2tsts1 );
  clus->setF0( f0 );
  clus->setF1( f1 );
  clus->setF2( f2 );
  clus->setF3( f3 );
  clus->setRhad( rhad );
  clus->setRhad1( rhad1 );
  // Only EM energy since this is a eletromagnetic cluster
  clus->setEt( clus->eta() != 0.0 ? (e0+e1+e2+e3)/cosh(fabs(clus->eta())) : 0.0 ); 
  clus->setE(e0+e1+e2+e3);
  // Rp Mapping
  clus->setRp0( rp0 );
  clus->setRp1( rp1 );
  clus->setRp2( rp2 );
  clus->setRp3( rp3 );
  clus->setRphad1( rphad1 );
  clus->setRphad2( rphad2 );
  clus->setRphad3( rphad3 );

  return StatusCode::SUCCESS;
}

//!=====================================================================

float ShowerShapes::sumEnergyEM( xAOD::CaloCluster *clus, int sampling, unsigned eta_ncell, unsigned phi_ncell ) const
{
  float energy = 0.0;
  for ( const auto& cell : clus->cells() )
  {
    const xAOD::CaloDetDescriptor* det = cell->descriptor();

    // Exclude all HEC, TILE cells from the loop...
    if (det->detector()!= Detector::TTEM) continue;

    // if PS, the cell must be PSE or PSB
    if(sampling==0 && (
      det->sampling()!=CaloSampling::PSB &&
      det->sampling()!=CaloSampling::PSE )  ) continue;

    // if EM1, this cell must be EMB1 or EMEC1
    if(sampling==1 && (
      det->sampling()!=CaloSampling::EMB1 &&
      det->sampling()!=CaloSampling::EMEC1 )  ) continue;

    // if EM2, this cell must be EMB2 or EMEC2
    if(sampling==2 && (
      det->sampling()!=CaloSampling::EMB2 &&
      det->sampling()!=CaloSampling::EMEC2 )  ) continue;

    // if EM3, this cell must be EMB3 or EMEC3
    if(sampling==3 && (
      det->sampling()!=CaloSampling::EMB3 &&
      det->sampling()!=CaloSampling::EMEC3 )  ) continue;


    float deltaEta = std::abs( clus->eta() - cell->eta() );
    float deltaPhi = std::abs( CaloPhiRange::fix( clus->phi() - cell->phi() ) );
    
    if( deltaEta < eta_ncell*(cell->deltaEta()/2) && deltaPhi < phi_ncell*(cell->deltaPhi()/2) ){
      energy+= cell->e();
    }
  }
  return energy;
}

//!=====================================================================

float ShowerShapes::sumEnergyHAD( xAOD::CaloCluster *clus, int sampling, unsigned eta_ncell, unsigned phi_ncell ) const
{
  float energy = 0.0;
  for ( const auto& cell : clus->cells() )
  {
    const xAOD::CaloDetDescriptor* det = cell->descriptor();

    // Exclude all EM cells from the loop...
    if (det->detector()== Detector::TTEM) continue;

    // HAD 1
    if(sampling==0 && 
    ( (det->sampling()!=CaloSampling::HEC1) &&
      (det->sampling()!=CaloSampling::TileCal1) &&
      (det->sampling()!=CaloSampling::TileExt1) ) ) continue;

    // HAD 2
    if(sampling==1 && 
    ( (det->sampling()!=CaloSampling::HEC2) &&
      (det->sampling()!=CaloSampling::TileCal2) &&
      (det->sampling()!=CaloSampling::TileExt2) ) ) continue;

    // HAD 3
    if(sampling==2 && 
    ( (det->sampling()!=CaloSampling::HEC3) &&
      (det->sampling()!=CaloSampling::TileCal3) &&
      (det->sampling()!=CaloSampling::TileExt3) ) ) continue;


    float deltaEta = std::abs( clus->eta() - cell->eta() );
    float deltaPhi = std::abs( CaloPhiRange::fix( clus->phi() - cell->phi() ) );
    
    if( deltaEta < eta_ncell*(cell->deltaEta()/2) && deltaPhi < phi_ncell*(cell->deltaPhi()/2) ){
      energy+= cell->e();
    }
  }
  return energy;
}

//!=====================================================================

float ShowerShapes::calculateWeta2( xAOD::CaloCluster *clus , unsigned eta_ncell, unsigned phi_ncell) const
{
  float En2=0.0;
  float En=0.0;
  float E=0.0;

  for ( auto& cell : clus->cells() ){

    const xAOD::CaloDetDescriptor* det = cell->descriptor();

    // Only EM2 cells should be used here...
    if(det->sampling()!=CaloSampling::EMB2 && det->sampling()!=CaloSampling::EMEC2)  continue;
    
    float deltaEta = std::abs( clus->eta() - cell->eta() );
    float deltaPhi = std::abs( CaloPhiRange::diff( clus->phi() , cell->phi() ) );
 
    if( deltaEta < eta_ncell*(cell->deltaEta()/2) && deltaPhi < phi_ncell*(cell->deltaPhi()/2) ){
      En2 += cell->e() * std::pow(cell->eta(),2);
      En += cell->e() * cell->eta();
      E += cell->e();
    }
  }// Loop over all cells inside of the cluster

  return std::sqrt( (En2/E) - std::pow( (En/E),2 ) );
}


float ShowerShapes::rpmapping( xAOD::CaloCluster *clus, int sampling, float alpha, float beta, float kappa, float gamma) const
{

  float eta_center =0;
  float phi_center =0;

  xAOD::CaloCell hotCell;
  if (sampling > 3) {         // If HAD1,HAD2,HAD3 then uses EM2 hot cell
    eta_center = clus->eta();
    phi_center = clus->phi();
  } else {                    // If not (PS, EM1...3) the uses the it own hot cell
    getHotCell(clus,sampling, hotCell);  
    eta_center = hotCell.eta();
    phi_center = hotCell.phi();
  }
  
  float num=0;
  float den=0;

  for ( auto& cell : clus->cells() ){
    const xAOD::CaloDetDescriptor* det = cell->descriptor();

    if(sampling==0 && (
      det->sampling()!=CaloSampling::PSB &&
      det->sampling()!=CaloSampling::PSE )  ) continue;

    // if EM1, this cell must be EMB1 or EMEC1
    if(sampling==1 && (
      det->sampling()!=CaloSampling::EMB1 &&
      det->sampling()!=CaloSampling::EMEC1 )  ) continue;

    // if EM2, this cell must be EMB2 or EMEC2
    if(sampling==2 && (
      det->sampling()!=CaloSampling::EMB2 &&
      det->sampling()!=CaloSampling::EMEC2 )  ) continue;

    // if EM3, this cell must be EMB3 or EMEC3
    if(sampling==3 && (
      det->sampling()!=CaloSampling::EMB3 &&
      det->sampling()!=CaloSampling::EMEC3 )  ) continue;
    
    if(sampling==4 && 
    ( (det->sampling()!=CaloSampling::HEC1) &&
      (det->sampling()!=CaloSampling::TileCal1) &&
      (det->sampling()!=CaloSampling::TileExt1) ) ) continue;

    // HAD 2
    if(sampling==5 && 
    ( (det->sampling()!=CaloSampling::HEC2) &&
      (det->sampling()!=CaloSampling::TileCal2) &&
      (det->sampling()!=CaloSampling::TileExt2) ) ) continue;

    // HAD 3
    if(sampling==6 && 
    ( (det->sampling()!=CaloSampling::HEC3) &&
      (det->sampling()!=CaloSampling::TileCal3) &&
      (det->sampling()!=CaloSampling::TileExt3) ) ) continue;
  
    // Rp Mapping

    float deta    = cell->eta() - eta_center;
    // double dphi = fabs(cell->phi() - phi_center) < M_PI ? fabs(cell->phi() - phi_center) : 2*M_PI - fabs(cell->phi() - phi_center);
    double dphi   = CaloPhiRange::diff(phi_center , cell->phi());
    float rdist   = sqrt(pow(kappa*deta,2) + pow(gamma*dphi,2));
    float r_beta  = pow(rdist,beta);
    float cell_e  = cell->e() < 0 ? 0 : cell->e();
    float e_alpha = pow(cell_e,alpha);
    
    num += e_alpha * r_beta;
    den += pow(cell_e,alpha);
    
  }

  return num/den;
}

bool ShowerShapes::getHotCell( xAOD::CaloCluster *clus, int sampling, xAOD::CaloCell &hotCell ) const {

    std::vector<float> cells_energy;

  for ( auto& cell : clus->cells() ){
    cells_energy.push_back(cell->e());
    }
   
   for ( auto& cell : clus->cells() ){
    const xAOD::CaloDetDescriptor* det = cell->descriptor();

    if(sampling==0 && (
      det->sampling()!=CaloSampling::PSB &&
      det->sampling()!=CaloSampling::PSE )  ) continue;

    // if EM1, this cell must be EMB1 or EMEC1
    if(sampling==1 && (
      det->sampling()!=CaloSampling::EMB1 &&
      det->sampling()!=CaloSampling::EMEC1 )  ) continue;

    // if EM2, this cell must be EMB2 or EMEC2
    if(sampling==2 && (
      det->sampling()!=CaloSampling::EMB2 &&
      det->sampling()!=CaloSampling::EMEC2 )  ) continue;

    // if EM3, this cell must be EMB3 or EMEC3
    if(sampling==3 && (
      det->sampling()!=CaloSampling::EMB3 &&
      det->sampling()!=CaloSampling::EMEC3 )  ) continue;
    
    if(sampling==4 && 
    ( (det->sampling()!=CaloSampling::HEC1) &&
      (det->sampling()!=CaloSampling::TileCal1) &&
      (det->sampling()!=CaloSampling::TileExt1) ) ) continue;

    // HAD 2
    if(sampling==5 && 
    ( (det->sampling()!=CaloSampling::HEC2) &&
      (det->sampling()!=CaloSampling::TileCal2) &&
      (det->sampling()!=CaloSampling::TileExt2) ) ) continue;

    // HAD 3
    if(sampling==6 && 
    ( (det->sampling()!=CaloSampling::HEC3) &&
      (det->sampling()!=CaloSampling::TileCal3) &&
      (det->sampling()!=CaloSampling::TileExt3) ) ) continue;

    
    auto maxElementIndex = std::max_element(cells_energy.begin(),cells_energy.end()) - cells_energy.begin();
    auto hotCellTemp = clus->cells().at(maxElementIndex);
    hotCell = *hotCellTemp;

    
   }
   return true;
}