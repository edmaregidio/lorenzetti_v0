#ifndef ShowerShapes_h
#define ShowerShapes_h

#include "GaugiKernel/AlgTool.h"
#include "GaugiKernel/EDM.h"
#include "CaloCluster/CaloClusterContainer.h"
#include "CaloCell/CaloCell.h"

class ShowerShapes : public Gaugi::AlgTool
{

  public:
    /** Constructor **/
    ShowerShapes( std::string );
    virtual ~ShowerShapes()=default;
    
    virtual StatusCode initialize() override;
    virtual StatusCode finalize() override;

    virtual StatusCode execute( SG::EventContext &ctx, Gaugi::EDM * ) const override;


  private:
 
    float calculateWeta2( xAOD::CaloCluster * , unsigned eta_ncell=3, unsigned phi_ncell=5 ) const;
    float sumEnergyEM( xAOD::CaloCluster *, int sampling, unsigned eta_ncell=1000, unsigned phi_ncell=1000 ) const;
    float sumEnergyHAD( xAOD::CaloCluster *, int sampling, unsigned eta_ncell=1000, unsigned phi_ncell=1000 ) const;
    float rpmapping( xAOD::CaloCluster *clus, int sampling, float alpha, float beta, float kappa, float gamma) const;
    bool  getHotCell( xAOD::CaloCluster *, int sampling, xAOD::CaloCell &) const;

    float m_alpha=2.02;
    float m_beta=0.38;
    float m_kappa=1;
    float m_gamma=1;

};

#endif




