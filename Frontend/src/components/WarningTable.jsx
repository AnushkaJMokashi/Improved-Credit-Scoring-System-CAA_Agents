import React from "react";

export default function WarningTable(props) {
  const filterLength = props.filterLength;
  const filteredAlerts = props.filteredAlerts;
  const resultData = props.resultData;
  
  return (
    <div className="d-flex justify-content-center">
      <div className="col-md-10">
        <h3 className="py-3 text-danger">WARNINGS :</h3>
        <div className="col-md-8">
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>Sr.</th>
                <th>Defaulter Name</th>
                <th>Current Debt Amount</th>
                <th>Over Due Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filterLength > 0 ? (
                filteredAlerts.map((alert, index) => (
                  <tr key={index}>
                    <th>{index + 1}</th>
                    <td>{alert.customer}</td>
                    <td>{alert.current_debt_amount}</td>
                    <td>
                      {
                        resultData.customerDetails.find(
                          (customer) =>
                            customer.Customer_Name === alert.customer
                        )?.due_date_current_debt
                      }
                    </td>
                    <td>{alert.alert} &nbsp;Warning</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="text-center">
                    <p className="fs-3 fw-bolder">No NPA Record Found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
