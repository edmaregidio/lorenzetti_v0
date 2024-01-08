#ifndef CaloRpRingsMaker_h
#define CaloRpRingsMaker_h

#include "CaloCell/enumeration.h"
#include "GaugiKernel/StatusCode.h"
#include "GaugiKernel/DataHandle.h"
#include "GaugiKernel/Algorithm.h"
#include "CaloRings/CaloRingsContainer.h"
#include "CaloCluster/CaloClusterContainer.h"


class RpRingSet{
  
    public:
      /*! Contructor */
      RpRingSet( std::vector<CaloSampling> &samplings , unsigned nrings, float deta, float dphi, int init );
      /*! Destructor */
      RpRingSet()=default;
      /*! Add the cell energy to the correct ring position in this RingSet */
      void push_back( const xAOD::CaloCell *, float eta_center, float phi_center, float rp);
      /*! Get the ringer shaper pattern for this RingSet */
      const std::vector<float>& rings() const;
      /*! Computing Rp values */
      double computeRp(const xAOD::CaloCluster *, const xAOD::CaloCell *, float eta_center, float phi_center, float alpha, float beta) ;
      /*! The number of rings in this RingSet */
      size_t size() const;
      /*! Sampling id */
      bool isValid( const xAOD::CaloCell*) const;
      /*! Zeroize all energy values */
      void clear();


    private:

      std::vector<float> m_rings;
      /*! Delta eta */
      float m_deta;
      /*! Delta phi */
      float m_dphi;
      /*! Sampling layer */
      std::vector<CaloSampling> m_samplings;

      int m_rpinit;
  };





class CaloRpRingsMaker : public Gaugi::Algorithm
{
  public:


    /** Constructor **/
    CaloRpRingsMaker( std::string );
    
    virtual ~CaloRpRingsMaker();
    
    virtual StatusCode initialize() override;

    virtual StatusCode bookHistograms( SG::EventContext &ctx ) const override;
    
    virtual StatusCode pre_execute( SG::EventContext &ctx ) const override;
    
    virtual StatusCode execute( SG::EventContext &ctx , const G4Step *step) const override;
    
    virtual StatusCode execute( SG::EventContext &ctx, int /*evt*/ ) const override;

    virtual StatusCode post_execute( SG::EventContext &ctx ) const override;
    
    virtual StatusCode fillHistograms( SG::EventContext &ctx ) const override;
    
    virtual StatusCode finalize() override;



  private:
 
    int m_maxRingSets;    
    int m_maxRingsAccumulated;
    float m_alpha;
    float m_beta;
    
    const xAOD::CaloCell* maxCell( const xAOD::CaloCluster*   , RpRingSet & ) const;
   
    std::string m_histPath;

    std::string m_clusterKey;
    std::string m_ringerKey;

    std::vector<float>  m_detaRings;
    std::vector<float>  m_dphiRings;
    std::vector<int>    m_nRings;

    std::vector<std::vector<int>>    m_layerRings;
    std::vector<int> m_rpInit;

    int m_outputLevel;
};

#endif




